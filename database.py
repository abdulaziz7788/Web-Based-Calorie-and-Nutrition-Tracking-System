import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Aboos123!",
    database="project"
)

cursor = db.cursor()
