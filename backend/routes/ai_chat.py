import requests
import re
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from database import get_db

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

SCHEMA_CONTEXT = """
The database is for a Metro Information System with the following tables:
- Passenger(passenger_id, name, age, gender, phone)
- Fare(fare_id, source_station_id, destination_station_id, fare_amount)
- Station(station_id, station_name, location, zone, line_id)
- Metro_Line(line_id, line_name, total_stations)
- Ticket(ticket_id, passenger_id, journey_date, fare_id)
- Train(train_id, train_name, capacity, line_id)
- Station_Facility(facility_id, station_id, facility_name)
- Route(route_id, source_station_id, destination_station_id, line_id)
"""

@router.post("/chat")
def ai_chat(request: ChatRequest, db = Depends(get_db)):
    """
    RAG-based AI Chat using LM Studio local model.
    """
    user_query = request.query
    
    # Step 1: Get SQL from LM Studio
    prompt = f"{SCHEMA_CONTEXT}\n\nUser asks: '{user_query}'\nWrite a valid MySQL query to answer this. Return ONLY the SQL query without any explanation or markdown formatting."
    
    try:
        response = requests.post(
            "http://localhost:1234/api/v1/chat",
            json={
                "model": "google/gemma-4-e2b",
                "system_prompt": "You are a SQL expert.",
                "input": prompt
            },
            timeout=20
        )
        if response.status_code != 200:
            return {"response": f"Failed to connect to LM Studio AI model. Ensure it is running on localhost:1234. Detail: {response.text}"}
            
        data = response.json()
        # LM Studio /api/v1/chat usually returns the text directly, or in a content/response/message field
        sql_query = data.get('content', data.get('response', data.get('message', str(data))))
        if isinstance(sql_query, dict) and 'content' in sql_query:
             sql_query = sql_query['content']
        sql_query = str(sql_query).strip()
        
        # Robust SQL extraction
        sql_match = re.search(r"```sql(.*?)```", sql_query, re.DOTALL | re.IGNORECASE)
        if sql_match:
            sql_query = sql_match.group(1).strip()
        else:
            sql_match = re.search(r"```(.*?)```", sql_query, re.DOTALL)
            if sql_match:
                sql_query = sql_match.group(1).strip()
            else:
                select_match = re.search(r"(SELECT.*?;)", sql_query, re.DOTALL | re.IGNORECASE)
                if select_match:
                    sql_query = select_match.group(1).strip()
                else:
                    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
    except Exception as e:
        return {"response": f"Error communicating with LM Studio: {e}"}

    # Step 2: Execute SQL
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(sql_query)
        db_results = cursor.fetchall()
    except Exception as e:
        cursor.close()
        return {"response": f"The AI generated an invalid SQL query: {sql_query}\\n\\nError: {e}"}
    finally:
        cursor.close()
        
    # Step 3: Summarize result using LM Studio
    summary_prompt = f"The user asked: '{user_query}'.\\nThe database query returned: {db_results}\\nProvide a brief, natural language answer to the user based on these results."
    
    try:
        summary_response = requests.post(
            "http://localhost:1234/api/v1/chat",
            json={
                "model": "google/gemma-4-e2b",
                "system_prompt": "You are a helpful Metro Information AI assistant.",
                "input": summary_prompt
            },
            timeout=20
        )
        data = summary_response.json()
        final_answer = data.get('content', data.get('response', data.get('message', str(data))))
        if isinstance(final_answer, dict) and 'content' in final_answer:
             final_answer = final_answer['content']
        final_answer = str(final_answer).strip()
        return {"response": final_answer}
    except Exception as e:
        return {"response": f"Here is the raw data (failed to summarize using AI): {db_results}"}
