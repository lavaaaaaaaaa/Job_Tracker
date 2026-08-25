import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# connection = psycopg2.connect(DATABASE_URL)

# print("database connected succesfully")

def get_connection():
    return psycopg2.connect(DATABASE_URL)