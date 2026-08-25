from fastapi import FastAPI
from models import Job
from database import get_connection


app = FastAPI() #create my application

@app.get("/") #Whe somebody sends a GET request to /, use function below
def home(): #is the function that runs
    return{"project" : "Jobtrack",
           "status":"Day 1",
           "developer":"lava"} #sends data back

@app.get("/about")
def about():
    return {"message": "Personal job application tracker"}

@app.post("/jobs")
def create_job(job: Job):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO jobs(company, role, status)
        VALUES (%s, %s, %s)
        RETURNING id;
        """,
        (job.company, job.role, job.status)
    )

    job_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return{
        "id":job_id,
        "company":job.company,
        "role":job.role,
        "status":job.status
    }

@app.get("/jobs")
def get_jobs():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, company, role, status
        FROM jobs;
        """
    )

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return[
        {
            "id":job[0],
            "company":job[1],
            "role":job[2],
            "status":job[3],
        }
        for job in jobs      
    ]