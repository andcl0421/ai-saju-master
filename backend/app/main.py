from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import List

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "사주 마스터 서버에 오신 것을 환영합니다!"}

