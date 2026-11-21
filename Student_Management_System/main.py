from fastapi import FastAPI, HTTPException, Path
from database import get_db
from schema import StudentCreate, StudentUpdate, StudentPatch, StudentResponse

app = FastAPI()


# ----------------------------------------
# POST - CREATE STUDENT
# ----------------------------------------
@app.post("/students", status_code=201)
def create_student(student: StudentCreate):

    with get_db() as conn:
        with conn.cursor() as curr:

            curr.execute(
                "SELECT id FROM students WHERE id=%s",
                (student.id,)
            )

            if curr.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="Student with this ID already exists"
                )

            query = """
                INSERT INTO students
                (id, name, age, department, semester, email, marks, city)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """

            curr.execute(
                query,
                (
                    student.id,
                    student.name,
                    student.age,
                    student.department,
                    student.semester,
                    student.email,
                    student.marks,
                    student.city
                )
            )

            conn.commit()

            return {"message": "Student created successfully"}


# ----------------------------------------
# GET - ALL STUDENTS
# ----------------------------------------
@app.get("/students", response_model=list[StudentResponse])
def get_students():

    with get_db() as conn:
        with conn.cursor() as curr:

            curr.execute("SELECT * FROM students ORDER BY id")

            data = curr.fetchall()

            return data


# ----------------------------------------
# GET - STUDENT BY ID
# ----------------------------------------
@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int = Path(..., gt=0, description="Student ID")
):

    with get_db() as conn:
        with conn.cursor() as curr:

            curr.execute(
                "SELECT * FROM students WHERE id=%s",
                (student_id,)
            )

            data = curr.fetchone()

            if data is None:
                raise HTTPException(
                    status_code=404,
                    detail="Student not found"
                )

            return data


# ----------------------------------------
# PUT - COMPLETE UPDATE
# ----------------------------------------
@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    student: StudentUpdate
):

    with get_db() as conn:
        with conn.cursor() as curr:

            curr.execute(
                "SELECT id FROM students WHERE id=%s",
                (student_id,)
            )

            if curr.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Student not found"
                )

            query = """
                UPDATE students
                SET name=%s,
                    age=%s,
                    department=%s,
                    semester=%s,
                    email=%s,
                    marks=%s,
                    city=%s
                WHERE id=%s
            """

            curr.execute(
                query,
                (
                    student.name,
                    student.age,
                    student.department,
                    student.semester,
                    student.email,
                    student.marks,
                    student.city,
                    student_id
                )
            )

            conn.commit()

            return {"message": "Student updated successfully"}


# ----------------------------------------
# PATCH - PARTIAL UPDATE
# ----------------------------------------
@app.patch("/students/{student_id}")
def patch_student(
    student_id: int,
    student: StudentPatch
):

    # Only provided fields will be included
    update_data = student.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    # Prevent explicitly provided null values
    if any(value is None for value in update_data.values()):
        raise HTTPException(
            status_code=422,
            detail="Fields cannot be null"
        )

    with get_db() as conn:
        with conn.cursor() as curr:

            curr.execute(
                "SELECT id FROM students WHERE id=%s",
                (student_id,)
            )

            if curr.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Student not found"
                )

            # Build update query using validated column names
            columns = list(update_data.keys())

            set_clause = ", ".join(
                f"{column}=%s" for column in columns
            )

            values = list(update_data.values())

            query = f"""
                UPDATE students
                SET {set_clause}
                WHERE id=%s
            """

            values.append(student_id)

            curr.execute(query, tuple(values))

            conn.commit()

            return {"message": "Student partially updated successfully"}


# ----------------------------------------
# DELETE - STUDENT
# ----------------------------------------
@app.delete("/students/{student_id}")
def delete_student(student_id: int):

    with get_db() as conn:
        with conn.cursor() as curr:

            curr.execute(
                "SELECT id FROM students WHERE id=%s",
                (student_id,)
            )

            if curr.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Student not found"
                )

            curr.execute(
                "DELETE FROM students WHERE id=%s",
                (student_id,)
            )

            conn.commit()

            return {"message": "Student deleted successfully"}