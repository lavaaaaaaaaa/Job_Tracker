from fastapi import FastAPI, HTTPException
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
        INSERT INTO jobs(company, role, status, location, work_mode,job_url, salary)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (job.company, job.role, job.status, job.location, job.work_mode, job.job_url, job.salary)
    )

    job_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return{
        "id":job_id,
        "company":job.company,
        "role":job.role,
        "status":job.status,
        "work_mode": job.work_mode,
        "job_url": job.job_url,
        "location": job.location,
        "salary" : job.salary
    }

@app.get("/jobs")
def get_jobs(
    status: str | None = None,
    work_mode: str |None = None
):
    connection = get_connection()
    cursor = connection.cursor()
 
    if status and work_mode:
        cursor.execute("""
            SELECT id, company, role, status, work_mode, job_url, location, salary
            FROM jobs
            WHERE LOWER(status) = LOWER(%s) 
            AND LOWER(work_mode) = LOWER(%s);
            """,
            (status, work_mode)
        )

    elif status:
        cursor.execute("""
            SELECT id, company, role, status, work_mode, job_url, location, salary
            FROM jobs
            WHERE LOWER(status) = LOWER(%s);
            """,
            (status,)
        )

    elif work_mode:
        cursor.execute("""
            SELECT id, company, role, status, work_mode, job_url, location, salary
            FROM jobs
            WHERE LOWER(work_mode) = LOWER(%s);
            """,
            (work_mode,)
        )

    else:
        cursor.execute("""
            SELECT id, company, role, status, work_mode, job_url, location, salary
            FROM jobs;
            """
        )

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return [
        {
            "id": job[0],
            "company": job[1],
            "role": job[2],
            "status": job[3],
            "work_mode": job[4],
            "job_url": job[5],
            "location": job[6],
            "salary": job[7],           
        }
        for job in jobs
    ]

@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, company, role, status, location, work_mode, job_url, salary
        FROM jobs
        WHERE id = %s;
        """,
        (job_id,)
    )

    job = cursor.fetchone()

    cursor.close()
    connection.close()

    if job is None:
        raise HTTPException(
            status_code = 404,
            detail = "Job not found"
        )


    return{
        "id":job[0],
        "company":job[1],
        "role":job[2],
        "status":job[3],
        "work_mode":job[4],
        "job_url":job[5],
        "location":job[6],
        "salary":job[7],
            
    }


@app.put("/jobs/{job_id}")
def update_job(job_id: int, job: Job):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE jobs
        SET company = %s,
            role = %s,
            status = %s,
            work_mode = %s,
            job_url = %s,
            location = %s,
            salary = %s
        WHERE id = %s
        RETURNING id, company, role, status, work_mode, job_url, location, salary;
        """,
        (job.company, job.role, job.status, job.work_mode, job.job_url, job.location, job.salary, job_id)
    )

    updated_job = cursor.fetchone()

    if updated_job is None:
        cursor.clode()
        connection.close()
        return {"message": "Job not found"}

    connection.commit()
    cursor.close()
    connection.close()

    return{
        "id": updated_job[0],
        "company": updated_job[1],
        "role": updated_job[2],
        "status": updated_job[3],
        "work_mode": updated_job[4],
        "job_url": updated_job[5],
        "location": updated_job[6],
        "salary": updated_job[7],
    }

@app.delete("/jobs/{job_id}")
def delete_job(job_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM jobs
        WHERE id = %s
        RETURNING id;
        """,
        (job_id,)
    )

    deleted_job = cursor.fetchone()

    if deleted_job is None:
        cursor.close()
        connection.close()
        return {"message": "Job not found"}

    connection.commit()
    cursor.close()
    connection.close()

    return{
        "message": "Job deleted successfully",
        "id": deleted_job[0]
    }

