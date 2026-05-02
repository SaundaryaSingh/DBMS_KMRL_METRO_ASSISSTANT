import mysql.connector

def create_database():
    # Connect to MySQL server (without specifying DB yet)
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin"
    )
    cursor = conn.cursor()

    # Drop and recreate database
    cursor.execute("DROP DATABASE IF EXISTS MetroDB;")
    cursor.execute("CREATE DATABASE MetroDB;")
    cursor.execute("USE MetroDB;")

    ddl_commands = [
        """
        CREATE TABLE Metro_Line(
            line_id INT PRIMARY KEY,
            line_name VARCHAR(50) NOT NULL,
            total_stations INT CHECK(total_stations > 0)
        );
        """,
        """
        CREATE TABLE Station(
            station_id INT PRIMARY KEY,
            station_name VARCHAR(50),
            location VARCHAR(50),
            zone VARCHAR(10),
            line_id INT,
            FOREIGN KEY(line_id) REFERENCES Metro_Line(line_id)
        );
        """,
        """
        CREATE TABLE Train(
            train_id INT PRIMARY KEY,
            train_name VARCHAR(50),
            capacity INT CHECK(capacity > 0),
            line_id INT,
            FOREIGN KEY(line_id) REFERENCES Metro_Line(line_id)
        );
        """,
        """
        CREATE TABLE Route(
            route_id INT PRIMARY KEY,
            source_station_id INT,
            destination_station_id INT,
            line_id INT,
            FOREIGN KEY(source_station_id) REFERENCES Station(station_id),
            FOREIGN KEY(destination_station_id) REFERENCES Station(station_id),
            FOREIGN KEY(line_id) REFERENCES Metro_Line(line_id)
        );
        """,
        """
        CREATE TABLE Schedule(
            schedule_id INT PRIMARY KEY,
            route_id INT,
            train_id INT,
            arrival_time TIME,
            departure_time TIME,
            FOREIGN KEY(route_id) REFERENCES Route(route_id),
            FOREIGN KEY(train_id) REFERENCES Train(train_id)
        );
        """,
        """
        CREATE TABLE Fare(
            fare_id INT PRIMARY KEY,
            source_station_id INT,
            destination_station_id INT,
            fare_amount DECIMAL(5,2) CHECK(fare_amount > 0),
            FOREIGN KEY(source_station_id) REFERENCES Station(station_id),
            FOREIGN KEY(destination_station_id) REFERENCES Station(station_id)
        );
        """,
        """
        CREATE TABLE Passenger(
            passenger_id INT PRIMARY KEY,
            name VARCHAR(50),
            age INT CHECK(age > 0),
            gender VARCHAR(10),
            phone VARCHAR(15) UNIQUE
        );
        """,
        """
        CREATE TABLE Ticket(
            ticket_id INT,
            passenger_id INT,
            journey_date DATE,
            fare_id INT,
            PRIMARY KEY(ticket_id, passenger_id),
            FOREIGN KEY(passenger_id) REFERENCES Passenger(passenger_id),
            FOREIGN KEY(fare_id) REFERENCES Fare(fare_id)
        );
        """,
        """
        CREATE TABLE Employee(
            emp_id INT PRIMARY KEY,
            name VARCHAR(50),
            role VARCHAR(30),
            salary DECIMAL(10,2) CHECK(salary > 0)
        );
        """,
        """
        CREATE TABLE Station_Facility(
            facility_id INT PRIMARY KEY,
            station_id INT,
            facility_name VARCHAR(50),
            FOREIGN KEY(station_id) REFERENCES Station(station_id)
        );
        """,
        # Normalized tables for Chapter 5 Transaction Demo
        """
        CREATE TABLE Passenger_2NF (
            passenger_id INT PRIMARY KEY,
            passenger_name VARCHAR(50),
            phone VARCHAR(15)
        );
        """,
        """
        CREATE TABLE Ticket_2NF (
            ticket_id INT,
            passenger_id INT,
            train_name VARCHAR(50),
            route VARCHAR(100),
            fare DECIMAL(5,2),
            PRIMARY KEY(ticket_id, passenger_id)
        );
        """,
        """
        CREATE TABLE Station_3NF (
            station_id INT PRIMARY KEY,
            station_name VARCHAR(50)
        );
        """,
        """
        CREATE TABLE Route_3NF (
            route_id INT PRIMARY KEY,
            source_station_id INT,
            destination_station_id INT
        );
        """,
        """
        CREATE TABLE Station_Facility_4NF (
            station_id INT,
            facility VARCHAR(50),
            PRIMARY KEY(station_id, facility)
        );
        """
    ]

    for ddl in ddl_commands:
        cursor.execute(ddl)

    # Insert Data
    dml_commands = [
        "INSERT INTO Metro_Line VALUES (1,'Red Line',15),(2,'Blue Line',15),(3,'Green Line',15);",
        # Including extra stations (5,6,7) to prevent foreign key errors for Route and Fare inserts
        "INSERT INTO Station VALUES (1,'Aluva','Kochi','A',1), (2,'Pulinchodu','Kochi','A',1), (3,'Companypady','Kochi','B',1), (5,'Station5','Kochi','C',1), (6,'Station6','Kochi','C',1), (7,'Station7','Kochi','C',1);",
        "INSERT INTO Train VALUES (1,'TrainA',200,1), (2,'TrainB',180,1), (3,'TrainC',220,2);",
        "INSERT INTO Passenger VALUES (1,'Rahul',21,'M','9999990001'), (2,'Riya',22,'F','9999990002'), (3,'Aman',23,'M','9999990003');",
        "INSERT INTO Route VALUES (1,1,5,1),(2,2,6,1),(3,3,7,1);",
        "INSERT INTO Schedule VALUES (1,1,1,'08:00:00','08:05:00'), (2,2,2,'08:10:00','08:15:00'), (3,3,3,'08:20:00','08:25:00');",
        "INSERT INTO Fare VALUES (1,1,5,20),(2,2,6,25),(3,3,7,30);",
        "INSERT INTO Ticket VALUES (1,1,'2026-03-01',1), (2,2,'2026-03-02',2), (3,3,'2026-03-03',3);",
        "INSERT INTO Employee VALUES (1,'Ravi','Manager',50000), (2,'Sita','Staff',30000), (3,'John','Security',25000);",
        "INSERT INTO Station_Facility VALUES (1,1,'Lift'), (2,1,'Escalator'), (3,2,'Parking');",

        # Transaction Data
        "INSERT INTO Passenger_2NF VALUES (1, 'Rahul', '9999990001'), (2, 'Riya', '9999990002');",
        "INSERT INTO Ticket_2NF VALUES (1, 1, 'TrainA', 'Aluva-Pulinchodu', 20), (2, 1, 'TrainB', 'Aluva-Companypady', 25), (3, 2, 'TrainA', 'Pulinchodu-Aluva', 20);",
        "INSERT INTO Station_3NF VALUES (1, 'Aluva'), (2, 'Pulinchodu'), (3, 'Companypady');",
        "INSERT INTO Route_3NF VALUES (1, 1, 5), (2, 2, 6), (3, 3, 7);",
        "INSERT INTO Station_Facility_4NF VALUES (1, 'Lift'), (1, 'Escalator'), (2, 'Parking');"
    ]

    for dml in dml_commands:
        cursor.execute(dml)
        
    # Create the views, triggers, and procedures mentioned in the report
    
    # 3.6 Views
    cursor.execute("CREATE VIEW HighFare AS SELECT * FROM Fare WHERE fare_amount > 50;")
    
    # 3.7 Triggers
    trigger_sql = """
    CREATE TRIGGER check_fare
    BEFORE INSERT ON Fare
    FOR EACH ROW
    BEGIN
     IF NEW.fare_amount < 0 THEN
     SIGNAL SQLSTATE '45000'
     SET MESSAGE_TEXT = 'Invalid Fare';
     END IF;
    END;
    """
    cursor.execute(trigger_sql)
    
    # 3.8 Cursors (Procedures)
    proc1_sql = """
    CREATE PROCEDURE GetPassengers()
    BEGIN
     SELECT * FROM Passenger;
    END;
    """
    cursor.execute(proc1_sql)
    
    proc2_sql = """
    CREATE PROCEDURE CursorExample()
    BEGIN
     DECLARE done INT DEFAULT FALSE;
     DECLARE pname VARCHAR(50);
     DECLARE cur CURSOR FOR SELECT name FROM Passenger;
     DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
     OPEN cur;
     read_loop: LOOP
     FETCH cur INTO pname;
     IF done THEN
     LEAVE read_loop;
     END IF;
     END LOOP;
     CLOSE cur;
    END;
    """
    cursor.execute(proc2_sql)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database MetroDB created and populated successfully.")

if __name__ == "__main__":
    create_database()
