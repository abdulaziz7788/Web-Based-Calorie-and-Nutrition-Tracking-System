import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="#", ######## put your database info here !!! 
    database="#" ###### Here too !!!
)

cursor = db.cursor()
