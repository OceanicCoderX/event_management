#!C:/Python314/python.exe
import cgitb
import mysql.connector
cgitb.enable()

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        port='3306',
        user='root',
        password='',
        database='event_management_db'
    )
