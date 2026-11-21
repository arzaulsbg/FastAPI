import json

with open("students.json",'r') as file:
    students=json.load(file)

for id, info in students.items():
    if info['age']==19:
        print(id,info)



student=[]
for student_id,info in students.items():
    info["id"]=student_id
    student.append(info)

student.sort(key=lambda x:x)
print(student)