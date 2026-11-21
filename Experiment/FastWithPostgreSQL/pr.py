import psycopg
from psycopg import connect
from psycopg.rows import dict_row
import csv
import os
from contextlib import closing
from dotenv import load_dotenv
load_dotenv()

db_url=os.getenv("DATABASE_URL")
def get_db():
    conn=connect(db_url,row_factory=dict_row)
    return conn


# with get_db() as conn:
#     version=conn.execute("select version()").fetchone()["version"]
#     print(version.split())

# def read_csv():
#     with open("students.csv") as file:
#         reader=csv.reader(file)
#         next(reader)
#         for i ,row in enumerate(reader,start=1):
#             print(f"rows: {i} values: {row}")

# read_csv()

# with get_db() as conn:
#     cur=conn.cursor()
#     query="""create table if not exists employees (id int primary key,name varchar(50),age int,depart varchar(30),semester varchar(30),email varchar(30) unique,marks float,city varchar(30))"""
#     cur.execute(query=query)
#     print("employee table successfully created")

# insert data in employee table

# with get_db() as conn:
#     curr=conn.cursor()
#     query="""insert into employees (id,name,age,depart,semester,email,marks,city) values(%s,%s,%s,%s,%s,%s,%s,%s)"""
#     # read data from students.csv file
#     with open("students.csv",'r') as file:
#         reader=csv.reader(file)
#         next(reader)
#         for row in reader:
#             curr.execute(query,row)
#         print("data inserted succesfully")


# display data from database
with closing(get_db()) as conn:
    cur=conn.cursor()
    query="select * from employees where city=%s"
    cur.execute(query,("Amritsar",))
    data=cur.fetchall()
    print((data))
    cur.close()

