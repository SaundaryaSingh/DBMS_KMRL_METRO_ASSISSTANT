from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_db

router = APIRouter()

@router.post("/reset")
def reset_transaction_tables(db = Depends(get_db)):
    """Reset the 2NF, 3NF, 4NF tables for fresh transaction demos."""
    cursor = db.cursor()
    try:
        # Clear data
        cursor.execute("DELETE FROM Ticket_2NF")
        cursor.execute("DELETE FROM Passenger_2NF")
        cursor.execute("DELETE FROM Route_3NF")
        cursor.execute("DELETE FROM Station_Facility_4NF")
        cursor.execute("DELETE FROM Station_3NF")

        # Insert original data
        cursor.execute("INSERT INTO Passenger_2NF VALUES (1, 'Rahul', '9999990001'), (2, 'Riya', '9999990002');")
        cursor.execute("INSERT INTO Ticket_2NF VALUES (1, 1, 'TrainA', 'Aluva-Pulinchodu', 20), (2, 1, 'TrainB', 'Aluva-Companypady', 25), (3, 2, 'TrainA', 'Pulinchodu-Aluva', 20);")
        cursor.execute("INSERT INTO Station_3NF VALUES (1, 'Aluva'), (2, 'Pulinchodu'), (3, 'Companypady');")
        cursor.execute("INSERT INTO Route_3NF VALUES (1, 1, 5), (2, 2, 6), (3, 3, 7);")
        cursor.execute("INSERT INTO Station_Facility_4NF VALUES (1, 'Lift'), (1, 'Escalator'), (2, 'Parking');")
        db.commit()
        return {"message": "Transaction tables reset successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

def execute_select(cursor, query):
    cursor.execute(query)
    return cursor.fetchall()

@router.get("/run/1")
def run_transaction_1(db = Depends(get_db)):
    """
    Transaction 1: Update passenger, savepoint A, insert, savepoint B, insert, rollback to A
    """
    db.start_transaction()
    cursor = db.cursor(dictionary=True)
    logs = []
    
    try:
        # Step 2
        cursor.execute("UPDATE Passenger_2NF SET passenger_name = 'Rahul Updated' WHERE passenger_id = 1")
        logs.append("Updated Passenger 1 to 'Rahul Updated'")
        
        # Step 3
        cursor.execute("SAVEPOINT A")
        logs.append("Created SAVEPOINT A")
        
        # Step 4
        cursor.execute("INSERT INTO Passenger_2NF VALUES (3, 'Aman', '7777')")
        logs.append("Inserted Passenger 3 ('Aman')")
        
        # Step 5
        cursor.execute("SAVEPOINT B")
        logs.append("Created SAVEPOINT B")
        
        # Step 6
        cursor.execute("INSERT INTO Passenger_2NF VALUES (4, 'Neha', '6666')")
        logs.append("Inserted Passenger 4 ('Neha')")
        
        # Step 8: Rollback to B
        cursor.execute("ROLLBACK TO B")
        logs.append("Rolled back to SAVEPOINT B")
        
        # Step 9: Rollback to A
        cursor.execute("ROLLBACK TO A")
        logs.append("Rolled back to SAVEPOINT A")
        
        db.commit()
        logs.append("Committed transaction")
        
        # Final state
        cursor.execute("SELECT * FROM Passenger_2NF")
        final_state = cursor.fetchall()
        
        return {"logs": logs, "final_state": final_state}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

@router.get("/run/2")
def run_transaction_2(db = Depends(get_db)):
    """
    Transaction 2: Update ticket fare, savepoint A, insert, savepoint B, invalid insert, rollback to B
    """
    db.start_transaction()
    cursor = db.cursor(dictionary=True)
    logs = []
    
    try:
        cursor.execute("UPDATE Ticket_2NF SET fare = 30 WHERE ticket_id = 1")
        logs.append("Updated Ticket 1 fare to 30")
        
        cursor.execute("SAVEPOINT A")
        logs.append("Created SAVEPOINT A")
        
        cursor.execute("INSERT INTO Ticket_2NF VALUES (4, 1, 'TrainC', 'RouteX', 40)")
        logs.append("Inserted Ticket 4")
        
        cursor.execute("SAVEPOINT B")
        logs.append("Created SAVEPOINT B")
        
        try:
            # Intentional wrong insert (assuming fare cannot be negative based on logic, but let's just trigger an error or rollback)
            # The report does: INSERT INTO Ticket_2NF VALUES (5,1,'Invalid',NULL,-10);
            cursor.execute("INSERT INTO Ticket_2NF VALUES (5, 1, 'Invalid', NULL, -10)")
            logs.append("Inserted Ticket 5 with negative fare")
        except Exception as e:
            logs.append(f"Error on Ticket 5 insert: {str(e)}")
            
        cursor.execute("ROLLBACK TO B")
        logs.append("Rolled back to SAVEPOINT B")
        
        db.commit()
        logs.append("Committed transaction")
        
        cursor.execute("SELECT * FROM Ticket_2NF")
        final_state = cursor.fetchall()
        
        return {"logs": logs, "final_state": final_state}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

@router.get("/state/{table}")
def get_table_state(table: str, db = Depends(get_db)):
    allowed_tables = ["Passenger_2NF", "Ticket_2NF", "Station_3NF", "Route_3NF", "Station_Facility_4NF"]
    if table not in allowed_tables:
        raise HTTPException(status_code=400, detail="Invalid table")
        
    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table}")
    res = cursor.fetchall()
    cursor.close()
    return res
