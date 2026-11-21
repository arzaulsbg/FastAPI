
from fastapi import FastAPI, HTTPException,Path,Query
import json
from pydantic import BaseModel,field_validator,Field,model_validator,EmailStr
app = FastAPI()

students = {
    1: {
        "name": "Arzaul",
        "age": 21,
        "course": "AI & Data Science"
    },
    2: {
        "name": "Rahul",
        "age": 22,
        "course": "B.Tech"
    },
    3: {
        "name": "Raju",
        "age": 25,
        "course": "BCA"
    }
}

app.get("/")(lambda: {"message": "Welcome to the Student API!"})
# GET
@app.get("/students")
def get_students():
    return students


# GET by ID
@app.get("/students/{student_id}")
def get_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404,
                            detail="Student not found")
    return students[student_id]


# POST
@app.post("/students", status_code=201)
def create_student(student_id: int, name: str, age: int):
    if student_id in students:
        raise HTTPException(status_code=400,
                            detail="Student already exists")

    students[student_id] = {
        "name": name,
        "age": age
    }

    return students[student_id]


# PUT
@app.put("/students/{student_id}")
def update_student(student_id: int, name: str, age: int):
    if student_id not in students:
        raise HTTPException(status_code=404,
                            detail="Student not found")

    students[student_id] = {
        "name": name,
        "age": age
    }

    return students[student_id]


# DELETE
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404,
                            detail="Student not found")

    del students[student_id]

    return {"message": "Student deleted successfully"}


with open("students.json",'r') as file:
    students=json.load(file)

@app.get("/stud")
def load_data():
    return students


@app.get("/stud/{student_id}")
def get_student(student_id:str=Path(...,description="This is student id")):
    if student_id not in students:
        raise HTTPException(detail=f"Id {student_id} not found",status_code=404)
    return students[student_id]

@app.get("/filter")
def filter_students(age:int=None):
    if age is None:
        return students
    filtered={}
    for id,info in students.items():
        if info["age"]==age:
            filtered[id]=info
    return filtered       

# sorting and ordering things
sort_field=['marks','age','name']
order_by=['asc','desc']
@app.get("/sort")
def sort_student(sort_by:str=Query(None,description="sort student by this",example="makrs or age")
                 ,order:str=Query(None,description="sort student asc or desc to this",example="asc or desc")):
    if sort_by not in sort_field:
        raise HTTPException(status_code=404,detail=f"invalid sort value choose from these{sort_field}")
    if order not in order_by:
        raise HTTPException(status_code=404,detail=f"invalid sort id choose from this {order_by}")

    #step-1 turn dic to list
    student=[]
    for student_id,info in students.items():
        info["id"]=student_id
        student.append(info)
    # step-2 sort the list by choosen field
    reversed=(order=="desc")
    sorted_student=sorted(student,key=lambda x:x[sort_by],reverse=reversed)
    return sorted_student
@app.get("/sorted")
def sort_student(sort_by:str=Query("marks",description="sort student by this",example="makrs or age")
                 ,order:str=Query("asc",description="sort student asc or desc to this",example="asc or desc")):
    if sort_by not in sort_field:
        raise HTTPException(status_code=404,detail=f"invalid sort value choose from these{sort_field}")
    if order not in order_by:
        raise HTTPException(status_code=404,detail=f"invalid sort id choose from this {order_by}")

    #step-1 turn dic to list
    student=[]
    for student_id,info in students.items():
        info["id"]=student_id
        student.append(info)
    # step-2 sort the list by choosen field
    reversed=(order=="desc")
    sorted_student=sorted(student,key=lambda x:x[sort_by],reverse=reversed)
    return sorted_student


# pagination
@app.get("/pagination")
def pagination(page:int=Query(1,ge=1,description="page number",example=1),limit:int=Query(2,ge=1,le=100,description="limit number",example=2)):
    start=(page-1)*limit
    end=start+limit
    student=[]
    for student_id,info in students.items():
        info["id"]=student_id
        student.append(info)
    return {
"page":page,
            "limit":limit,
            "total":len(student),
            "data":student[start:end]
    }

# "S020": {
#     "name": "Ayesha Ali",
#     "age": 20,
#     "course": "Computer Science",
#     "email": "ayesha@example.com",
#     "marks": 86
#   }
def load_Data():
    with open("students.json",'r') as file:
        students=json.load(file)
    return students
def save_data(data):
    with open("students.json",'w') as file:
        json.dump(data,file,indent=4)
class studentModel(BaseModel):
    id:str=Field(...,min_length=3)
    name:str=Field(...,min_length=3,max_length=40)
    age:int=Field(...,ge=10,le=100)
    course:str=Field(...,min_length=3,max_length=20)
    marks:int=Field(...,ge=0,le=100)
    phone:str|None=None

@app.post("/create",status_code=201)
def fun(student:studentModel):
    allStudent=load_Data()
    for id,info in allStudent.items():
        if info["name"]==student.name:
            raise HTTPException(status_code=400,detail=f"student with name {student.name} already exists")
    allStudent[student.id]=student.model_dump(exclude={"id","phone"})
    save_data(allStudent)
    return {"message":"student data saved successfully",
            "student":student.model_dump()}