from fastapi import APIRouter, Depends
from pydantic import BaseModel
from database import get_db

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

@router.post("/chat")
def ai_chat(request: ChatRequest, db = Depends(get_db)):
    """
    Mock endpoint for RAG-based AI Chat.
    In a real scenario, this would use LangChain + OpenAI/Gemini to translate the text to SQL,
    execute it against `db`, and return a natural language response.
    """
    user_query = request.query.lower()
    
    # Simple keyword-based mock responses
    if "total passengers" in user_query:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM Passenger")
        res = cursor.fetchone()
        cursor.close()
        return {"response": f"Based on the database, there are currently {res['total']} registered passengers in the KMRL system."}
        
    elif "average fare" in user_query:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT AVG(fare_amount) AS avg_fare FROM Fare")
        res = cursor.fetchone()
        cursor.close()
        return {"response": f"The average fare across all routes is ₹{float(res['avg_fare']):.2f}."}
        
    elif "stations" in user_query and "zone" in user_query:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT zone, COUNT(*) AS count FROM Station GROUP BY zone")
        res = cursor.fetchall()
        cursor.close()
        zones_str = ", ".join([f"Zone {r['zone']} has {r['count']} stations" for r in res])
        return {"response": f"Here is the breakdown of stations by zone: {zones_str}."}
        
    elif "metro lines" in user_query or "lines" in user_query:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT line_name FROM Metro_Line")
        res = cursor.fetchall()
        cursor.close()
        lines_str = ", ".join([r['line_name'] for r in res])
        return {"response": f"The KMRL currently operates the following lines: {lines_str}."}

    else:
        return {
            "response": "I am a simulated AI assistant for the KMRL Metro System. I can answer questions about total passengers, average fares, stations by zone, and metro lines. For full text-to-SQL functionality, an LLM API key integration is required."
        }
