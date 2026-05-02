import mysql.connector
db = mysql.connector.connect(host='localhost', user='root', password='admin', database='MetroDB')
cursor = db.cursor(dictionary=True)
cursor.execute('SELECT * FROM Ticket_2NF')
print('Before DELETE:', cursor.fetchall())
cursor.execute('DELETE FROM Ticket_2NF WHERE ticket_id >= 4')
db.commit()
cursor.execute('SELECT * FROM Ticket_2NF')
print('After DELETE:', cursor.fetchall())
