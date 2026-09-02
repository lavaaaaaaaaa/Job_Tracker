import os
import jwt

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import Job, UserCreate, UserLogin, Token
from database import get_connection
from pwdlib import PasswordHash
# from argon2 import PasswordHasher

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI() #create my application
ph = PasswordHash.recommended()

def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return token

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return int(user_id)

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

@app.get("/") #Whe somebody sends a GET request to /, use function below
def home(): #is the function that runs
    return{"project" : "Jobtrack",
           "status":"Day 1",
           "developer":"lava"} #sends data back

@app.get("/about")
def about():
    return {"message": "Personal job application tracker"}

@app.post("/register")
def register(user: UserCreate):
    connection = get_connection()
    cursor = connection.cursor()

    password_hash = ph.hash(user.password)

    cursor.execute(
        """
        INSERT INTO users(username, email, password_hash)
        VALUES (%s, %s, %s)
        RETURNING id, username, email;
        """,
        (user.username, user.email, password_hash)
    )

    new_user = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()
    return{
        "id": new_user[0],
        "username": new_user[1],
        "email": new_user[2]
    }

@app.get("/users/me")
def get_me(user_id: int = Depends(get_current_user)):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, username, email
        FROM users
        WHERE id = %s;
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user[0],
        "username": user[1],
        "email": user[2]
    }

@app.post("/token", response_model = Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, username, email, password_hash
        FROM users
        WHERE username = %s;
        """,
        (form_data.username,)
    )

    db_user = cursor.fetchone()
    cursor.close()
    connection.close()

    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail = "Invalid email or password"
        )

    try:
        ph.verify(form_data.password, db_user[3])

    except:
        raise HTTPException(
            status_code=401,
            detail = "Invalid email or password"
        )
    access_token = create_access_token(db_user[0])
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    # return {
    #     "message": "Login successful",
    #     "user_id": db_user[0],
    #     "email": db_user[1]
    # }

@app.post("/jobs")
def create_job(
    job: Job,
    user_id: int = Depends(get_current_user)):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO jobs(company, role, status, location, work_mode,job_url, salary, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (job.company, job.role, job.status, job.location, job.work_mode, job.job_url, job.salary, user_id)
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
    work_mode: str |None = None,
    user_id: int = Depends(get_current_user)
):
    connection = get_connection()
    cursor = connection.cursor()
 
    if status and work_mode:
        cursor.execute("""
            SELECT id, company, role, status, work_mode, job_url, location, salary
            FROM jobs
            WHERE user_id = %s
            AND LOWER(status) = LOWER(%s) 
            AND LOWER(work_mode) = LOWER(%s);
            """,
            (user_id, status, work_mode)
        )

    elif status:
        cursor.execute("""
            SELECT id, company, role, status, work_mode, job_url, location, salary
            FROM jobs
            WHERE user_id = %s
            AND LOWER(status) = LOWER(%s);
            """,
            (user_id, status,)
        )

    elif work_mode:
        cursor.execute("""
            SELECT id, company, role, status, work_mode, job_url, location, salary
            FROM jobs
            WHERE user_id = %s
            AND LOWER(work_mode) = LOWER(%s);
            """,
            (user_id, work_mode,)
        )

    else:
        cursor.execute("""
            SELECT id, company, role, status, work_mode, job_url, location, salary
            FROM jobs
            WHERE user_id = %s;
            """,
            (user_id,)
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
def get_job(job_id: int,
    user_id: int = Depends(get_current_user)):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, company, role, status, location, work_mode, job_url, salary
        FROM jobs
        WHERE id = %s
        AND user_id = %s;
        """,
        (job_id, user_id)
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
def update_job(job_id: int, job: Job, user_id: int = Depends(get_current_user)):
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
        AND user_id = %s
        RETURNING id, company, role, status, work_mode, job_url, location, salary;
        """,
        (job.company, job.role, job.status, job.work_mode, job.job_url, job.location, job.salary, job_id, user_id)
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
def delete_job(job_id: int, user_id: int = Depends(get_current_user)):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM jobs
        WHERE id = %s
        AND user_id = %s
        RETURNING id;
        """,
        (job_id, user_id)
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

