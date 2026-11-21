import os
from contextlib import contextmanager
import csv
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extras import RealDictCursor

load_dotenv()

db_url = os.getenv("DATABASE_URL")


@contextmanager
def get_db():
    conn = connect(
        db_url,
        cursor_factory=RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.close()


# def insert_data():

#     with open("students.csv",'r') as file:
#         reader=csv.reader(file)
#         next(reader)
#         with get_db() as conn:
#             with conn.cursor() as curr:
#                 query=query="""insert into students (id,name,age,department,semester,email,marks,city) values(%s,%s,%s,%s,%s,%s,%s,%s)"""
#                 for row in reader:
#                     curr.execute(query,row)

#             conn.commit()
#         print("data inserted succefuuly")

# insert_data()