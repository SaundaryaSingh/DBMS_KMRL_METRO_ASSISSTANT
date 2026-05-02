import requests
import re
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from database import get_db

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

SCHEMA_CONTEXT = """
The database is for a Metro Information System (KMRL) with the following tables:
- Passenger(passenger_id, name, age, gender, phone)
- Fare(fare_id, source_station_id, destination_station_id, fare_amount)
- Station(station_id, station_name, location, zone, line_id)
- Metro_Line(line_id, line_name, total_stations)
- Ticket(ticket_id, passenger_id, journey_date, fare_id)
- Train(train_id, train_name, capacity, line_id)
- Station_Facility(facility_id, station_id, facility_name)
- Route(route_id, source_station_id, destination_station_id, line_id)
"""

LM_STUDIO_URL = "http://localhost:1234/api/v1/chat"
MODEL = "google/gemma-4-e2b"


def call_lm_studio(system_prompt: str, user_input: str) -> str:
    """Call LM Studio and return the text content from the output."""
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": MODEL,
            "system_prompt": system_prompt,
            "input": user_input,
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()

    # Primary format: {'output': [{'type': 'reasoning', ...}, {'type': 'message', 'content': '...'}]}
    # ALWAYS pick the 'message' type item — never the 'reasoning' item.
    if "output" in data and isinstance(data["output"], list):
        for item in data["output"]:
            if item.get("type") == "message":
                return str(item.get("content", "")).strip()
        # Fallback: take last item if no 'message' type found
        if data["output"]:
            return str(data["output"][-1].get("content", "")).strip()

    # Fallback for other API formats
    return str(data.get("content", data.get("response", data.get("message", "")))).strip()


def extract_sql(raw: str) -> str | None:
    """
    Robustly extract a SQL SELECT/CALL statement from the model output.
    Returns None if no valid SQL is found.
    """
    # 1. Try ```sql ... ``` blocks
    m = re.search(r"```sql\s*(.*?)```", raw, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # 2. Try generic ``` ... ``` blocks
    m = re.search(r"```\s*(SELECT|CALL|INSERT|UPDATE|DELETE)(.*?)```", raw, re.DOTALL | re.IGNORECASE)
    if m:
        return (m.group(1) + m.group(2)).strip()

    # 3. Try to find a SELECT/CALL statement — with OR without semicolon
    m = re.search(
        r"(SELECT\s+.+?(?:;|$)|CALL\s+\w+\(.*?\)\s*;?)",
        raw,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        sql = m.group(1).strip()
        # Strip any trailing non-SQL prose after the last meaningful token
        # e.g. "SELECT * FROM Passenger\n\nNote: this returns all passengers"
        sql = re.split(r"\n\s*\n", sql)[0].strip()
        return sql.rstrip(";").strip() + ";"   # normalise semicolon

    return None


@router.post("/chat")
async def ai_chat(request: ChatRequest, db=Depends(get_db)):
    """
    RAG-based AI Chat using LM Studio local model with streaming.
    """
    user_query = request.query

    def generate():
        # ── Step 1: Decide if this is a data query or just a greeting ──────────
        classify_raw = call_lm_studio(
            system_prompt=(
                "You are a classifier. Reply with EXACTLY one word: "
                "'DATA' if the user is asking for information from a database, "
                "or 'CHAT' if it is a greeting or conversational message."
            ),
            user_input=user_query,
        )
        intent = "DATA" if "DATA" in classify_raw.upper() else "CHAT"

        if intent == "CHAT":
            # Just answer conversationally
            answer = call_lm_studio(
                system_prompt="You are the KMRL Metro AI Assistant. Greet the user warmly and tell them they can ask questions about passengers, fares, stations, trains, or tickets.",
                user_input=user_query,
            )
            yield f"data: {json.dumps({'text': answer})}\n\n"
            return

        # ── Step 2: Generate SQL ────────────────────────────────────────────────
        sql_raw = call_lm_studio(
            system_prompt=(
                "You are a MySQL expert for a Metro Information System. "
                "Output ONLY a single valid MySQL SELECT or CALL statement. "
                "No explanation, no markdown, no comments. Just raw SQL."
            ),
            user_input=(
                f"Database schema:\n{SCHEMA_CONTEXT}\n\n"
                f"Write a MySQL query to answer: {user_query}"
            ),
        )

        sql_query = extract_sql(sql_raw)

        if not sql_query:
            yield f"data: {json.dumps({'text': 'I could not generate a valid SQL query for that question. Please try rephrasing.'})}\n\n"
            return

        # ── Step 3: Execute SQL ─────────────────────────────────────────────────
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute(sql_query)
            db_results = cursor.fetchall()
            cursor.close()
        except Exception as e:
            yield f"data: {json.dumps({'text': f'I had trouble querying the database. The SQL was: `{sql_query}`\\n\\nError: {e}'})}\n\n"
            return

        # ── Step 4: Summarise in natural language ───────────────────────────────
        summary = call_lm_studio(
            system_prompt=(
                "You are the KMRL Metro Assistant. Answer the user's question "
                "in one or two sentences using only the data provided. "
                "Be direct, friendly, and do NOT repeat the raw data or any SQL."
            ),
            user_input=(
                f"User asked: '{user_query}'\n"
                f"Query result: {db_results}\n"
                "Answer:"
            ),
        )

        # Stream the final summary word-by-word so it feels live
        words = summary.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == 0 else " " + word
            yield f"data: {json.dumps({'text': chunk})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
