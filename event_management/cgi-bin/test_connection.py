#!C:/Python314/python.exe
import sys
sys.path.append('.')
from db_config import get_connection

try:
    conn = get_connection()
    print('Connection successful')
    conn.close()
except Exception as e:
    print('Connection error:', str(e))