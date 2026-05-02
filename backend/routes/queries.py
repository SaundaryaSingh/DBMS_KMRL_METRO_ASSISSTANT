from fastapi import APIRouter, Depends, HTTPException
from database import get_db

router = APIRouter()

def execute_query(conn, query, params=None):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

# 3.2 Aggregate Functions
@router.get("/aggregate/total-passengers")
def get_total_passengers(db = Depends(get_db)):
    return execute_query(db, "SELECT COUNT(*) AS Total_Passengers FROM Passenger")

@router.get("/aggregate/average-fare")
def get_average_fare(db = Depends(get_db)):
    return execute_query(db, "SELECT AVG(fare_amount) AS Avg_Fare FROM Fare")

@router.get("/aggregate/stations-per-zone")
def get_stations_per_zone(db = Depends(get_db)):
    return execute_query(db, "SELECT zone, COUNT(*) AS Station_Count FROM Station GROUP BY zone HAVING COUNT(*) > 2")

# 3.3 Sets
@router.get("/sets/station-facilities-unique")
def get_unique_stations_facilities(db = Depends(get_db)):
    query = """
    SELECT station_name as name FROM Station
    UNION
    SELECT facility_name as name FROM Station_Facility
    """
    return execute_query(db, query)

@router.get("/sets/station-facilities-all")
def get_all_stations_facilities(db = Depends(get_db)):
    query = """
    SELECT station_name as name FROM Station
    UNION ALL
    SELECT facility_name as name FROM Station_Facility
    """
    return execute_query(db, query)

@router.get("/sets/stations-not-source")
def get_stations_not_source(db = Depends(get_db)):
    query = """
    SELECT station_id FROM Station
    WHERE station_id NOT IN (
        SELECT source_station_id FROM Fare
    )
    """
    return execute_query(db, query)

# 3.4 Subqueries
@router.get("/subqueries/fares-above-average")
def get_fares_above_average(db = Depends(get_db)):
    query = """
    SELECT * FROM Fare
    WHERE fare_amount > (
        SELECT AVG(fare_amount) FROM Fare
    )
    """
    return execute_query(db, query)

@router.get("/subqueries/passengers-with-tickets")
def get_passengers_with_tickets(db = Depends(get_db)):
    query = """
    SELECT * FROM Passenger
    WHERE passenger_id IN (
        SELECT passenger_id FROM Ticket
    )
    """
    return execute_query(db, query)

@router.get("/subqueries/passengers-above-average-age")
def get_passengers_above_avg_age(db = Depends(get_db)):
    query = """
    SELECT * FROM Passenger
    WHERE age > (
        SELECT AVG(age) FROM Passenger
    )
    """
    return execute_query(db, query)

# 3.5 Joins
@router.get("/joins/passenger-tickets")
def get_passenger_tickets(db = Depends(get_db)):
    query = """
    SELECT p.name, t.ticket_id
    FROM Passenger p
    INNER JOIN Ticket t
    ON p.passenger_id = t.passenger_id
    """
    return execute_query(db, query)

@router.get("/joins/station-fares")
def get_station_fares(db = Depends(get_db)):
    query = """
    SELECT s.station_name, f.fare_amount
    FROM Station s
    LEFT JOIN Fare f
    ON s.station_id = f.source_station_id
    """
    return execute_query(db, query)

@router.get("/joins/stations-same-line")
def get_stations_same_line(db = Depends(get_db)):
    query = """
    SELECT A.station_name as station1, B.station_name as station2
    FROM Station A, Station B
    WHERE A.line_id = B.line_id
    AND A.station_id <> B.station_id
    """
    return execute_query(db, query)

# 3.6 Views
@router.get("/views/high-fare")
def get_high_fare_view(db = Depends(get_db)):
    return execute_query(db, "SELECT * FROM HighFare")

# 3.8 Cursors / Procedures
@router.get("/cursors/get-passengers")
def call_get_passengers_proc(db = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.callproc('GetPassengers')
        results = []
        for result_set in cursor.stored_results():
            results.extend(result_set.fetchall())
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

# Extra route to fetch all tables data for the frontend dashboard
@router.get("/dashboard-data")
def get_dashboard_data(db = Depends(get_db)):
    data = {
        "lines": execute_query(db, "SELECT * FROM Metro_Line"),
        "stations": execute_query(db, "SELECT * FROM Station"),
        "trains": execute_query(db, "SELECT * FROM Train"),
        "passengers": execute_query(db, "SELECT * FROM Passenger"),
    }
    return data
