import urllib
import os
import sqlalchemy
from dotenv import load_dotenv

load_dotenv()

database = 'your_database_name'
username = os.getenv('SQL_SERVER_ADMIN_USER')
password = os.getenv('SQL_SERVER_ADMIN_PW')
driver = '{ODBC Driver 17 for SQL Server}'
server = os.getenv('SQL_SERVER')

pyodbc_conn_str = f'Driver={driver};Server={server};Database=exploring-database;Uid={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

# Establish connection
params = urllib.parse.quote_plus(pyodbc_conn_str)
engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")


