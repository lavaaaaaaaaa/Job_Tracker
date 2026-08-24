from fastapi import FastAPI
app = FastAPI() #create my application
@app.get("/") #Whe somebody sends a GET request to /, use function below
def home(): #is the function that runs
    return{"project" : "Jobtrack",
           "status":"Day 1",
           "developer":"lava"} #sends data back
@app.get("/about")
def about():
    return {"message": "Personal job application tracker"}