import os
import csv
from  psycopg.rows import dict_row
from psycopg import connect
from dotenv import load_dotenv
load_dotenv()

Db_url=os.getenv("DATABASE_URL")
# print(Db_url)

def get_db():
    conn=connect(Db_url,row_factory=dict_row)
    # try:
    #     yield conn
    # finally:
    #     conn.close()
    return conn
# with get_db() as conn:

#     version=conn.execute("SELECT version()").fetchone()["version"]
# # print(version.split()[0])

# with get_db() as conn:
#     cur=conn.cursor()
#     cur.execute("create table  if not exists students(id serial primary key ,name varchar(40),age INT)")
#     conn.commit()
#     print("table is created")

# with get_db() as conn:
#     cur=conn.cursor()
#     cur.execute("Insert into students (name,age)values(%s,%s)",("Rahul",21))
#     conn.commit()
#     cur.close()
#     conn.close()
#     print("Student inserted !")

# # store existing data
# students = [
#     ("Rahul", 21),
#     ("Aman", 22),
#     ("Priya", 20),
#     ("Simran", 23)
# ]


# query="insert into students (name,age) values(%s,%s)"
# conn=get_db()
# curr=conn.cursor()
# curr.executemany(query,students)
# conn.commit()
# print("Students inserted successfully !")
# # display data
# curr.execute("SELECT * FROM students")
# conn.close()
# data=curr.fetchall()
# for row in data:
#     print(row)

# read csv

conn=get_db()
# conn.execute("""CREATE TABLE if not exists student (
#     student_id INT PRIMARY KEY,
#     name VARCHAR(100) NOT NULL,
#     age INT,
#     department VARCHAR(100),
#     semester VARCHAR(20),
#     email VARCHAR(150) UNIQUE,
#     marks FLOAT,
#     city VARCHAR(100)
# )""")




conn.commit()
conn.close()
conn=get_db()
cur=conn.cursor()
with open("students.csv",'r') as file:
    render=csv.reader(file)
    next(render)
    query="insert into student (student_id,name,age,department,semester,email,marks,city) values(%s,%s,%s,%s,%s,%s,%s,%s)"
    for row in render:
        cur.execute(query,row)

conn.commit()
cur.close()
conn.close()
print("student data store successfully")