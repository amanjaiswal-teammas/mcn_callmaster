import json
import os
import re
import secrets

import uuid
from urllib.request import Request

import aiofiles
import jwt
import datetime
import bcrypt
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Header, Query
from fastapi.exceptions import RequestValidationError
from sqlalchemy import create_engine, Column, Integer, String, func, DateTime, text, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr, constr, validator
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from pathlib import Path
from datetime import date, timedelta
from pydantic import BaseModel
from typing import List, Optional, Dict
import pandas as pd
from transcriber import transcribe_with_deepgram_async
from analyzer import analyze_transcript
from dashboard3_ptp_routes import router as dashboard3_router
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
# from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

SECRET_KEY = "your_secret_key"

# class SecurityHeadersMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         response: Response = await call_next(request)
#         response.headers["X-Frame-Options"] = "DENY"
#         response.headers["Content-Security-Policy"] = (
#             "default-src 'self'; "
#             "img-src 'self' data: https:; "
#             "script-src 'self' https://cdnjs.cloudflare.com; "
#             "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
#             "font-src 'self' https://fonts.gstatic.com; "
#             "frame-ancestors 'none';"
#         )
#         response.headers["X-Content-Type-Options"] = "nosniff"
#         return response
#
# app.add_middleware(SecurityHeadersMiddleware)


# CORS Middleware to allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(dashboard3_router)
# MySQL Database Connection (replace with your actual credentials)
# SQL_DB_URL = "mysql+pymysql://root:Hello%40123@localhost/my_db?charset=utf8mb4"
SQL_DB_URL = "mysql+pymysql://root:dial%40mas123@172.12.10.22/ai_audit?charset=utf8mb4"
engine = create_engine(SQL_DB_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

#########  Second DB

# DATABASE_URL2 = "mysql+pymysql://root:321*#LDtr!?*ktasb@192.168.10.12/db_dialdesk"
#DATABASE_URL2 = "mysql+pymysql://root:321%2A%23LDtr%21%3F%2Aktasb@192.168.10.22/db_dialdesk"
DATABASE_URL2 = "mysql+pymysql://root:vicidialnow@192.168.10.6/db_audit"

# Create SQLAlchemy engine
engine2 = create_engine(DATABASE_URL2)
SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)


# Dependency to get database session
def get_db2():
    db = SessionLocal2()
    try:
        yield db
    finally:
        db.close()


#########  Third DB

DATABASE_URL3 = "mysql+pymysql://root:vicidialnow@192.168.10.6/db_external"

# Create SQLAlchemy engine

engine3 = create_engine(DATABASE_URL3)

SessionLocal3 = sessionmaker(autocommit=False, autoflush=False, bind=engine3)


# Dependency to get database session

def get_db3():
    db = SessionLocal3()
    try:
        yield db
    finally:
        db.close()


# User Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email_id = Column(String(255), unique=True, nullable=False)
    contact_number = Column(String(15), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=True)
    clientid = Column(String, nullable=True)
    set_limit = Column(Integer, nullable=False, default=30)
    company_name = Column(String(255), nullable=True)
    leadid = Column(String(50), nullable=True)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


# Pydantic Models for Request Body
class UserRequest(BaseModel):
    username: str
    email_id: EmailStr
    contact_num: constr(min_length=10, max_length=15)  # Removed regex from constr()
    password: str
    confirm_password: str

    @validator("contact_num")
    def validate_contact_num(cls, value):
        """Ensure contact number contains only digits."""
        if not re.match(r"^\d+$", value):
            raise ValueError("Contact number must contain only digits")
        return value

    @validator("confirm_password")
    def passwords_match(cls, confirm_password, values):
        """Ensure password and confirm_password match."""
        if "password" in values and confirm_password != values["password"]:
            raise ValueError("Passwords do not match")
        return confirm_password


class LoginRequest(BaseModel):
    email_id: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email_id: EmailStr


class ResetPasswordRequest(BaseModel):
    email_id: EmailStr
    new_password: str
    confirm_password: str


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()

    error_message = errors[0]["msg"] if errors else "Validation error."

    error_message = error_message.replace("Value error, ", "")

    return JSONResponse(status_code=400, content={"detail": error_message})


class UserRequest(BaseModel):
    username: str
    email_id: EmailStr
    contact_number: str
    password: str
    confirm_password: str
    company_name: str

    @validator("contact_number")
    def validate_phone(cls, value):
        if not re.fullmatch(r"^\d{10}$", value):
            raise ValueError("Phone number must have exactly 10 digits.")
        return value


class TempUser(Base):
    __tablename__ = "temp_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=False, nullable=False)
    email_id = Column(String, unique=True, nullable=False)
    contact_number = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    otp = Column(String, nullable=False)
    otp_expiry = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    mobile_otp = Column(String, nullable=False)


class OTPVerifyRequest(BaseModel):
    email_id: str
    contact_number: str
    otp: str
    mobile_otp: str


def generate_otp():
    return str(random.randint(100000, 999999))





@app.post("/api/register")
def register_user(user: UserRequest, db: Session = Depends(get_db)):
    # Check if email or phone already exists in temp or main users
    if db.query(TempUser).filter(
            (TempUser.email_id == user.email_id) | (TempUser.contact_number == user.contact_number)).first():
        raise HTTPException(status_code=400, detail="OTP already sent. Please verify.")

    if db.query(User).filter(User.email_id == user.email_id).first():
        raise HTTPException(status_code=400, detail="Email is already registered. Use a different one.")

    if db.query(User).filter(User.contact_number == user.contact_number).first():
        raise HTTPException(status_code=400, detail="Phone number is already registered. Use a different one.")

    otp = str(random.randint(100000, 999999))
    mobile_otp = "123456"

    otp_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)  # OTP valid for 10 minutes

    # ? Hash the password BEFORE storing it in TempUser
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    temp_user = TempUser(
        username=user.username,
        email_id=user.email_id,
        contact_number=user.contact_number,
        password=hashed_password,  # ? Store hashed password directly
        company_name=user.company_name,
        otp=otp,
        otp_expiry=otp_expiry,
        mobile_otp=mobile_otp
    )

    db.add(temp_user)
    db.commit()

    # Send OTP via email & SMS
    send_otp_email(user.email_id, otp)
    send_otp_sms(user.contact_number, otp)

    return {"detail": "OTP sent to registered email and mobile.", "email_id": user.email_id,
            "contact_number": user.contact_number}


# from datetime import datetime, timedelta


@app.post("/api/verify-otp-login")
def verify_otp_login(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    temp_user = db.query(TempUser).filter(
        (TempUser.email_id == request.email_id) &
        (TempUser.contact_number == request.contact_number)
    ).first()

    if not temp_user:
        raise HTTPException(status_code=400, detail="Invalid request. Please register first.")

    if temp_user.otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid Email OTP.")

    if temp_user.mobile_otp != request.mobile_otp:
        raise HTTPException(status_code=400, detail="Invalid Mobile OTP.")

    # ? Don't hash again, just move the existing hashed password
    new_user = User(
        username=temp_user.username,
        email_id=temp_user.email_id,
        contact_number=temp_user.contact_number,
        password=temp_user.password,  # ? Use already hashed password
        company_name=temp_user.company_name
    )

    db.add(new_user)
    db.commit()

    db.delete(temp_user)
    db.commit()

    return {"detail": "User verified and registered successfully."}


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def otp_email(email, otp):
    sender_email = "sachinkr78276438@gmail.com"
    sender_password = "efsn ryss yjin kwgr"

    smtp_server = "smtp.example.com"
    smtp_port = 587

    subject = "Your OTP for Verification"
    body = f"Your OTP is: {otp}. It is valid for 10 minutes."

    # Constructing the email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)  # Login to email account
        server.sendmail(sender_email, email, msg.as_string())  # Send email
        server.quit()  # Close connection

        print(f"? OTP sent to {email}")
        return True
    except Exception as e:
        print(f"? Error sending email: {e}")
        return False


def send_otp_sms(phone, otp):
    # Use an SMS API like Twilio, Nexmo, etc.
    pass


# @app.post("/register")
# def register_user(user: UserRequest, db: Session = Depends(get_db)):
#     if user.password != user.confirm_password:
#         raise HTTPException(status_code=400, detail="Passwords do not match.")
#
#     if db.query(User).filter(User.username == user.username).first():
#         raise HTTPException(status_code=400, detail="Username is already taken. Choose another one.")
#
#     if db.query(User).filter(User.email_id == user.email_id).first():
#         raise HTTPException(status_code=400, detail="Email is already registered. Use a different one.")
#
#     if db.query(User).filter(User.contact_number == user.contact_number).first():
#         raise HTTPException(status_code=400, detail="Phone number is already registered. Use a different one.")
#
#     hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
#
#     new_user = User(
#         username=user.username,
#         email_id=user.email_id,
#         contact_number=user.contact_number,
#         password=hashed_password,
#         company_name=user.company_name  # Added company name field
#     )
#
#     try:
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#
#     return {"detail": "User registered successfully."}


# Route to Login a User
@app.post("/api/login")
def login_user(user: LoginRequest, db: Session = Depends(get_db)):
    # Check if the user exists based on email
    db_user = db.query(User).filter(User.email_id == user.email_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the password matches
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Generate JWT Token for session management
    # token = jwt.encode(
    #     {"email_id": user.email_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
    #     SECRET_KEY,
    #     algorithm="HS256"
    # )
    token = ''

    return {"message": "Login successful", "token": token, "username": db_user.username, "id": db_user.id,
            "client_id": db_user.clientid,
            "set_limit": db_user.set_limit,
            "contact_number": db_user.contact_number,
            "leadid": db_user.leadid}


class VerifyOtpRequest(BaseModel):
    email_id: str  # The user's email address
    otp: int


import random
import smtplib
from email.mime.text import MIMEText

# Store OTPs temporarily (in a real app, use Redis or a DB)
otp_store = {}


def send_otp_email(email_id, otp):
    sender_email = "sachinkr78276438@gmail.com"  # Replace with your Gmail address
    sender_password = "efsn ryss yjin kwgr"  # Replace with your Gmail App Password
    subject = "Your Password Reset OTP"
    body = f"Your OTP for password reset is: {otp}. It is valid for 10 minutes."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = email_id

    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email_id, msg.as_string())
        server.quit()
        print(f"OTP sent to {email_id}")
    except Exception as e:
        print(f"Error sending email: {e}")


@app.post("/api/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email_id == request.email_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = random.randint(100000, 999999)  # Generate 6-digit OTP
    otp_store[request.email_id] = {"otp": otp, "expires": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}

    send_otp_email(request.email_id, otp)

    return {"message": "OTP has been sent to your email. It is valid for 10 minutes."}


@app.post("/api/verify-otp")
def verify_otp(request: VerifyOtpRequest):
    stored_data = otp_store.get(request.email_id)

    if not stored_data:
        raise HTTPException(status_code=400, detail="OTP expired or not requested.")

    if stored_data["otp"] != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    # Mark OTP as verified (for security)
    otp_store[request.email_id]["verified"] = True

    return {"message": "OTP verified successfully. You can now reset your password."}


@app.post("/api/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    stored_data = otp_store.get(request.email_id)

    if not stored_data or not stored_data.get("verified"):
        raise HTTPException(status_code=400, detail="OTP not verified.")

    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    user = db.query(User).filter(User.email_id == request.email_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.password = hashed_password

    db.commit()

    # Remove OTP after password reset
    del otp_store[request.email_id]

    return {"message": "Password has been successfully reset"}


# Define the "prompts" table
class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    ClientId = Column(Integer, nullable=False)
    PromptName = Column(String(255), nullable=False)
    prompt = Column(String(500), nullable=False)


# Define a request model to accept JSON input
class PromptRequest(BaseModel):
    ClientId: int
    PromptName: str
    prompt: str


# Create a new prompt
from fastapi import HTTPException


@app.post("/api/prompts/")
def create_prompt(request: PromptRequest, db: Session = Depends(get_db)):
    print("Received request:", request.dict())

    # Extract data from the request model
    ClientId = request.ClientId
    PromptName = request.PromptName
    prompt = request.prompt

    if not ClientId or not PromptName or not prompt:
        raise HTTPException(status_code=400, detail="All fields are required")

    new_prompt = Prompt(ClientId=ClientId, PromptName=PromptName, prompt=prompt)
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)

    return new_prompt


class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(255), nullable=False)
    upload_time = Column(DateTime, server_default=func.now())
    transcribe_stat = Column(Integer, default=0)
    language = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    transcript = Column(String, nullable=True)
    user_id = Column(Integer, nullable=True, default=None)  # Can be NULL if not assigned
    minutes = Column(DECIMAL(5, 2), nullable=False, default=0.00)


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "ocr-frontend/public/audio"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed MIME types
ALLOWED_MIME_TYPES = ["audio/mpeg", "audio/wav"]
TRANSCRIBE_API_URL = "http://127.0.0.1:8095/transcribe"
import shutil
import httpx


@app.post("/api/upload-audio/")
async def upload_audio(
        files: list[UploadFile] = File(...),  # Accept multiple files
        language: str = Form(None),  # Optional field
        category: str = Form(None),  # Optional field
        user_id: int = Form(...),
        db: Session = Depends(get_db)
):
    uploaded_files = []

    try:
        for file in files:
            if file.content_type not in ALLOWED_MIME_TYPES:
                return {"status": 400, "message": f"Invalid file type: {file.filename}"}

            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Call Transcription API
            transcript_text = "No Transcript Available"
            transcribe_value = 0  # Default value if no transcript found
            formatted_minutes = 0.00

            try:
                with open(file_path, "rb") as audio_file:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(TRANSCRIBE_API_URL, files={"file": audio_file})

                if response.status_code == 200:
                    transcript_data = response.json()
                    print(f"Transcript response: {transcript_data}")  # Debugging

                    if isinstance(transcript_data, dict) and "transcript" in transcript_data:
                        transcript = transcript_data["transcript"]
                        duration = transcript_data.get("duration", 0)
                        minutes = int(duration) // 60
                        seconds = int(duration) % 60
                        minutes_decimal = minutes + (seconds / 60)

                        formatted_minutes = round(minutes_decimal, 2)

                        # Check if transcript is empty
                        if not transcript or transcript.strip() == "":
                            print("Empty transcript received, setting transcribe_value to 0")
                            transcript_text = "No Transcript Available"
                            transcribe_value = 0
                        else:
                            transcript_text = transcript
                            transcribe_value = 1  # Valid transcript found

                else:
                    print(f"Transcription API failed for {file.filename}, Status: {response.status_code}")

            except Exception as e:
                print(f"Error calling transcription API: {str(e)}")

            # Save to database
            new_audio = AudioFile(
                filename=file.filename,
                filepath=file_path,
                language=language,
                category=category,
                transcript=transcript_text,
                transcribe_stat=transcribe_value,
                user_id=user_id,
                minutes=formatted_minutes

            )
            db.add(new_audio)
            db.commit()
            db.refresh(new_audio)

            uploaded_files.append({
                "id": new_audio.id,
                "filename": new_audio.filename,
                "language": new_audio.language,
                "category": new_audio.category,
                "message": "File uploaded successfully"
            })

        return {"uploaded_files": uploaded_files}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


########## Curl fun ##############
class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # Ensure correct UUID format
    api_key = Column(String(64), unique=True, nullable=False, index=True)  # Unique and non-null
    created_at = Column(DateTime, server_default=func.now())
    status = Column(String(20), default="Active")


API_SECRET_TOKEN = "YOUR_SECRET_TOKEN"


class GenerateKeyRequest(BaseModel):
    user_id: str


class KeyResponse(BaseModel):
    user_id: int
    key: str
    api_secret_token: str
    # created_at: datetime
    # status: str


@app.post("/api/generate-key/", response_model=KeyResponse)
def generate_key(request: GenerateKeyRequest, db: Session = Depends(get_db)):
    global API_SECRET_TOKEN  # Allow modification of the global variable

    # Fetch user from the User table
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a new API key
    new_key = secrets.token_hex(16)
    API_SECRET_TOKEN = new_key  # Update global API_SECRET_TOKEN

    print(new_key, "Generated Key")
    print(API_SECRET_TOKEN, "Updated API_SECRET_TOKEN")

    # Save the new key in the database
    new_key_record = APIKey(api_key=new_key)
    db.add(new_key_record)
    db.commit()
    db.refresh(new_key_record)

    user.api_key = new_key_record.api_key
    db.commit()
    db.refresh(user)

    return {"user_id": user.id, "key": new_key_record.api_key, "api_secret_token": API_SECRET_TOKEN}


@app.post("/api/delete-key/{api_key}")
def delete_api_key(api_key: str, db: Session = Depends(get_db)):
    print("Received key to delete:", api_key)

    key_record = db.query(APIKey).filter(APIKey.api_key == api_key).first()

    if not key_record:
        raise HTTPException(status_code=404, detail="API key not found")

    user = db.query(User).filter(User.api_key == api_key).first()
    if user:
        user.api_key = None
        db.commit()

    db.delete(key_record)
    db.commit()

    return {"message": "API key deleted successfully"}


@app.post("/api/api/upload-audio-curl/")
async def upload_audio_curl(
        files: list[UploadFile] = File(...),
        language: str = Form(None),
        category: str = Form(None),
        user_id: int = Form(...),
        authorization: str = Header(None),
        db: Session = Depends(get_db)
):
    """Handles audio file upload, transcription, and database storage."""
    global API_SECRET_TOKEN  # Ensure we use the updated token
    # Validate Authorization
    if not authorization or authorization.split(" ")[-1] != API_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Token")

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    uploaded_files = []

    try:
        for file in files:
            print(f"Received file: {file.filename}, Content-Type: {file.content_type}")

            # Validate file type
            if file.content_type not in ALLOWED_MIME_TYPES:
                raise HTTPException(status_code=400,
                                    detail=f"Invalid file type: {file.filename} (Content-Type: {file.content_type})")

            # Save file
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Transcribe audio file
            transcript_text = "No Transcript Available"  # Default
            transcribe_value = 0  # Default value (0 = No Transcript)
            formatted_minutes = 0.00

            try:
                with open(file_path, "rb") as audio_file:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(TRANSCRIBE_API_URL, files={"file": audio_file})

                if response.status_code == 200:
                    transcript_data = response.json()
                    print(f"Transcript response: {transcript_data}")  # Debugging

                    if isinstance(transcript_data, dict):
                        transcript = transcript_data.get("transcript", "").strip()
                        duration = transcript_data.get("duration", 0)

                        # Convert duration (seconds) to decimal minutes
                        minutes = int(duration) // 60
                        seconds = int(duration) % 60
                        formatted_minutes = round(minutes + (seconds / 60), 2)

                        # Check transcript validity
                        if transcript:
                            transcript_text = transcript
                            transcribe_value = 1

                else:
                    print(f"Transcription API failed for {file.filename}, Status: {response.status_code}")

            except Exception as e:
                print(f"Error calling transcription API: {str(e)}")

            # Save file details and transcript to database
            new_audio = AudioFile(
                filename=file.filename,
                filepath=file_path,
                language=language,
                category=category,
                transcript=transcript_text,
                transcribe_stat=transcribe_value,
                user_id=user_id,  # Ensure user ID is saved
                minutes=formatted_minutes
            )
            db.add(new_audio)
            db.commit()
            db.refresh(new_audio)

            uploaded_files.append({
                "id": new_audio.id,
                "filename": new_audio.filename,
                "language": new_audio.language,
                "category": new_audio.category,
                "message": "File uploaded successfully"
            })

        return {"uploaded_files": uploaded_files}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# API to fetch records based on date range
class AudioStatsRequest(BaseModel):
    from_date: datetime.date
    to_date: datetime.date


@app.post("/api/api/get-audio-stats/")
def get_audio_stats(request: AudioStatsRequest, db: Session = Depends(get_db)):
    try:
        results = (
            db.query(
                func.date(AudioFile.upload_time).label("date"),
                func.count().label("upload"),
                func.sum(func.if_(AudioFile.transcribe_stat == 1, 1, 0)).label("transcribe")
            )
            .filter(func.date(AudioFile.upload_time).between(request.from_date, request.to_date))
            .group_by(func.date(AudioFile.upload_time))
            .all()
        )

        data_dict = {row.date: {"upload": row.upload, "transcribe": row.transcribe} for row in results}

        date_range = [
            (request.from_date + datetime.timedelta(days=i)) for i in
            range((request.to_date - request.from_date).days + 1)
        ]

        data = [
            {
                "date": str(date),
                "upload": data_dict.get(date, {"upload": 0, "transcribe": 0})["upload"],
                "transcribe": data_dict.get(date, {"upload": 0, "transcribe": 0})["transcribe"]
            }
            for date in date_range
        ]

        return {"status": "success", "data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/api/audit_count")
def get_audit_count(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today

    query = text("""
    SELECT
        COUNT(lead_id) AS audit_cnt,
        ROUND(
            SUM(CASE WHEN scenario2 <> 'Blank Call' THEN quality_percentage ELSE 0 END) / 
            NULLIF(COUNT(CASE WHEN scenario2 <> 'Blank Call' THEN lead_id END), 0), 
            2
        ) AS cq_score,
        SUM(CASE WHEN quality_percentage BETWEEN 98 AND 100 THEN 1 ELSE 0 END) AS excellent_call,
        SUM(CASE WHEN quality_percentage BETWEEN 90 AND 97 THEN 1 ELSE 0 END) AS good_call,
        SUM(CASE WHEN quality_percentage BETWEEN 85 AND 89 THEN 1 ELSE 0 END) AS avg_call,
        SUM(CASE WHEN quality_percentage <= 84 THEN 1 ELSE 0 END) AS below_avg_call
    FROM call_quality_assessment 
    WHERE ClientId = :client_id
    AND DATE(CallDate) BETWEEN :start_date AND :end_date;
    """)

    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchone()

    # Handle None case to avoid errors
    if not result:
        return {"audit_cnt": 0, "cq_score": 0, "excellent": 0, "good": 0, "avg_call": 0, "b_avg": 0}

    return {
        "audit_cnt": result[0] or 0,
        "cq_score": result[1] or 0.0,
        "excellent": result[2] or 0,
        "good": result[3] or 0,
        "avg_call": result[4] or 0,
        "b_avg": result[5] or 0
    }


@app.get("/api/call_length_categorization")
def get_call_length_categorization(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text("""
    SELECT 
    CASE
        WHEN length_in_sec < 60 THEN 'Short(<60sec)'
        WHEN length_in_sec BETWEEN 60 AND 300 THEN 'Average(1min-5min)'
        WHEN length_in_sec BETWEEN 301 AND 600 THEN 'Long(5min-10min)'
        ELSE 'Extremely Long(>10min)'
    END AS category,
    COUNT(*) AS audit_count,
    ROUND(
        100.0 * SUM(CASE WHEN professionalism_maintained = 0 AND scenario2 <> 'Blank Call' THEN 1 ELSE 0 END) 
        / NULLIF(COUNT(*), 0), 2
    ) AS fatal_percentage,
    ROUND(AVG(quality_percentage), 2) AS score_percentage
FROM call_quality_assessment
WHERE ClientId = :client_id
AND DATE(CallDate) BETWEEN :start_date AND :end_date
GROUP BY category
WITH ROLLUP; """)

    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchall()

    response_data = []
    for row in result:
        category = row[0] if row[0] else "Grand Total"
        response_data.append({
            "ACH Category": category,
            "Audit Count": row[1] or 0,
            "Fatal%": f"{row[2] or 0}%",
            "Score%": f"{row[3] or 0}%"
        })

    return response_data


@app.get("/api/agent_scores")
def get_agent_scores(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text("""
        SELECT 
            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    WHEN customer_concern_acknowledged = TRUE THEN 1
                    ELSE 0
                END
            ), 2) AS opening,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    ELSE 
                        (IF(professionalism_maintained = TRUE, 0.111111, 0) +
                         IF(assurance_or_appreciation_provided = TRUE, 0.111111, 0) +
                         IF(express_empathy = TRUE, 0.111111, 0) +
                         IF(pronunciation_and_clarity = TRUE, 0.111111, 0) +
                         IF(enthusiasm_and_no_fumbling = TRUE, 0.111111, 0) +
                         IF(active_listening = TRUE, 0.111111, 0) +
                         IF(politeness_and_no_sarcasm = TRUE, 0.111111, 0) +
                         IF(proper_grammar = TRUE, 0.111111, 0) +
                         IF(accurate_issue_probing = TRUE, 0.111111, 0))
                END
            ), 2) AS soft_skills,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    ELSE 
                        (IF(proper_hold_procedure = TRUE, 0.5, 0) +
                         IF(proper_transfer_and_language = TRUE, 0.5, 0))
                END
            ), 2) AS hold_procedure,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    ELSE 
                        (IF(address_recorded_completely = TRUE, 0.5, 0) +
                         IF(correct_and_complete_information = TRUE, 0.5, 0))
                END
            ), 2) AS resolution,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    WHEN professionalism_maintained = TRUE THEN 1
                    ELSE 0
                END
            ), 2) AS closing,

            ROUND((
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        WHEN customer_concern_acknowledged = TRUE THEN 1
                        ELSE 0
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        ELSE 
                            (IF(professionalism_maintained = TRUE, 0.111111, 0) +
                             IF(assurance_or_appreciation_provided = TRUE, 0.111111, 0) +
                             IF(express_empathy = TRUE, 0.111111, 0) +
                             IF(pronunciation_and_clarity = TRUE, 0.111111, 0) +
                             IF(enthusiasm_and_no_fumbling = TRUE, 0.111111, 0) +
                             IF(active_listening = TRUE, 0.111111, 0) +
                             IF(politeness_and_no_sarcasm = TRUE, 0.111111, 0) +
                             IF(proper_grammar = TRUE, 0.111111, 0) +
                             IF(accurate_issue_probing = TRUE, 0.111111, 0))
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        ELSE 
                            (IF(proper_hold_procedure = TRUE, 0.5, 0) +
                             IF(proper_transfer_and_language = TRUE, 0.5, 0))
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        ELSE 
                            (IF(address_recorded_completely = TRUE, 0.5, 0) +
                             IF(correct_and_complete_information = TRUE, 0.5, 0))
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        WHEN professionalism_maintained = TRUE THEN 1
                        ELSE 0
                    END
                )
            ) / 5, 2) AS avg_score

        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date;
    """)

    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchone()

    return {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date,
        "opening": result[0] * 100,
        "soft_skills": result[1] * 100,
        "hold_procedure": result[2] * 100,
        "resolution": result[3] * 100,
        "closing": result[4] * 100,
        "avg_score": result[5] * 100
    }


@app.get("/api/top_performers")
def get_top_performers(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text("""
        SELECT 
            User,
            COUNT(*) AS audit_count,
            ROUND(AVG(quality_percentage), 2) AS cq_percentage,
            SUM(CASE WHEN professionalism_maintained = 0 AND scenario2 <> 'Blank Call' THEN 1 ELSE 0 END) AS fatal_count,
            ROUND(SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) * 100, 2) AS fatal_percentage
        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        GROUP BY User
        ORDER BY cq_percentage DESC, audit_count DESC
        LIMIT 5;
    """)

    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchall()

    top_performers = [
        {
            "User": row[0],
            "audit_count": row[1],
            "cq_percentage": row[2],
            "fatal_count": row[3],
            "fatal_percentage": row[4]
        }
        for row in result
    ]

    return {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date,
        "top_performers": top_performers
    }


# Pydantic Model for Response
class CQScoreTrend(BaseModel):
    date: str  # Convert date to string format
    cq_score: float
    target: int


class CQScoreResponse(BaseModel):
    client_id: str
    target_cq: int
    trend: List[CQScoreTrend]


@app.get("/api/target_vs_cq_trend", response_model=CQScoreResponse)
def get_target_vs_cq_trend(
        client_id: str = Query(..., description="Client ID"),
        db: Session = Depends(get_db2)
):
    target_cq = 95  # Target CQ Score

    # Define date range (last 7 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=6)

    query = text("""
        SELECT DATE(CallDate) AS date, 
               ROUND(AVG(quality_percentage), 2) AS cq_score
        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        GROUP BY DATE(CallDate)
        ORDER BY DATE(CallDate) ASC;
    """)

    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchall()

    # Ensure all dates in the range are present, even with missing data
    trend_data = []
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        cq_score = next((row[1] for row in result if row[0] == current_date), 0)  # Default to 0 if no data
        trend_data.append(CQScoreTrend(date=current_date.strftime("%Y-%m-%d"), cq_score=cq_score, target=target_cq))

    return CQScoreResponse(client_id=client_id, target_cq=target_cq, trend=trend_data)


class PotentialEscalation(BaseModel):
    social_media_threat: int
    consumer_court_threat: int
    potential_scam: int


class NegativeSignals(BaseModel):
    abuse: int
    threat: int
    frustration: int
    slang: int
    sarcasm: int


class EscalationResponse(BaseModel):
    client_id: str
    potential_escalation: PotentialEscalation
    negative_signals: NegativeSignals


@app.get("/api/potential_escalation", response_model=EscalationResponse)
def get_potential_escalation(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text("""
        SELECT
            SUM(CASE WHEN LOWER(sensetive_word) LIKE '%social%' THEN 1 ELSE 0 END) AS social_media_threat,
            SUM(CASE WHEN LOWER(sensetive_word) LIKE '%court%'
                        OR LOWER(sensetive_word) LIKE '%consumer%'
                        OR LOWER(sensetive_word) LIKE '%legal%'
                        OR LOWER(sensetive_word) LIKE '%fir%' THEN 1 ELSE 0 END) AS consumer_court_threat,
            SUM(CASE WHEN system_manipulation = 'Yes' THEN 1 ELSE 0 END) AS potential_scam,

            SUM(CASE WHEN LOWER(top_negative_words) LIKE '%Abuse%' THEN 1 ELSE 0 END) AS abuse,
            SUM(CASE WHEN LOWER(top_negative_words) LIKE '%Threat%' THEN 1 ELSE 0 END) AS threat,
            SUM(CASE WHEN LOWER(top_negative_words) LIKE '%Frustration%' THEN 1 ELSE 0 END) AS frustration,
            SUM(CASE WHEN LOWER(top_negative_words) LIKE '%Slang%' THEN 1 ELSE 0 END) AS slang,
            SUM(CASE WHEN LOWER(top_negative_words) LIKE '%Sarcasm%' THEN 1 ELSE 0 END) AS sarcasm

        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
    """)

    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchone()

    return EscalationResponse(
        client_id=client_id,
        potential_escalation=PotentialEscalation(
            social_media_threat=result[0],
            consumer_court_threat=result[1],
            potential_scam=result[2]
        ),
        negative_signals=NegativeSignals(
            abuse=result[3],
            threat=result[4],
            frustration=result[5],
            slang=result[6],
            sarcasm=result[7]
        )
    )


@app.get("/api/potential_escalations_data/")
def get_potential_escalations_data(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text("""
        SELECT 
            scenario, 
            scenario1, 
            sensetive_word
        FROM call_quality_assessment
        WHERE ClientId = :client_id  
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        AND (
            LOWER(sensetive_word) LIKE '%social%'
            OR LOWER(sensetive_word) LIKE '%court%'
            OR LOWER(sensetive_word) LIKE '%consumer%'
            OR LOWER(sensetive_word) LIKE '%legal%'
            OR LOWER(sensetive_word) LIKE '%fir%'
            OR system_manipulation = 'Yes'
        )
    """)

    result = db.execute(query, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchall()

    return [
        {
            "scenario": row[0],
            "scenario1": row[1],
            "sensetive_word": row[2]
        }
        for row in result
    ]


@app.get("/api/negative_data/")
def get_negative_data(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text("""
        SELECT 
            scenario, 
            scenario1, 
            top_negative_words,lead_id,date(CallDate) call_date
        FROM call_quality_assessment
        WHERE ClientId = :client_id  
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        AND (
            LOWER(top_negative_words) LIKE '%Abuse%'
            OR LOWER(top_negative_words) LIKE '%Threat%'
            OR LOWER(top_negative_words) LIKE '%Frustration%'
            OR LOWER(top_negative_words) LIKE '%Slang%'
            OR LOWER(top_negative_words) LIKE '%Sarcasm%'
        )
    """)

    result = db.execute(query, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchall()

    return [
        {
            "scenario": row[0],
            "scenario1": row[1],
            "sensetive_word": row[2],
            "lead_id": row[3],
            "call_date": row[4]
        }
        for row in result
    ]


class ComplaintSummary(BaseModel):
    date: str  # Convert date to string format
    social_media_threat: int
    consumer_court_threat: int
    total: int


class ComplaintRawData(BaseModel):
    date: str  # Convert date to string format
    scenario: str
    sub_scenario: str
    sensitive_word: str


class ComplaintResponse(BaseModel):
    client_id: str
    summary: List[ComplaintSummary]
    raw_data: List[ComplaintRawData]


@app.get("/api/complaints_by_date", response_model=ComplaintResponse)
def get_complaints_by_date(
        client_id: str = Query(..., description="Client ID"),
        db: Session = Depends(get_db2)
):
    end_date = date.today()
    start_date = end_date - timedelta(days=6)

    summary_query = text("""
        SELECT 
            DATE(CallDate) AS date,
            SUM(CASE WHEN LOWER(sensetive_word) LIKE '%social%' THEN 1 ELSE 0 END) AS social_media_threat,
            SUM(CASE WHEN LOWER(sensetive_word) LIKE '%court%' 
                        OR LOWER(sensetive_word) LIKE '%consumer%' 
                        OR LOWER(sensetive_word) LIKE '%legal%' 
                        OR LOWER(sensetive_word) LIKE '%fir%' THEN 1 ELSE 0 END) AS consumer_court_threat,
            COUNT(*) AS total
        FROM call_quality_assessment
        WHERE ClientId = :client_id  
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        GROUP BY DATE(CallDate)
        ORDER BY DATE(CallDate) ASC;
    """)

    raw_data_query = text("""
        SELECT 
            DATE(CallDate) AS date,
            lead_id,
            sensetive_word AS sensitive_word,
            sensitive_word_context
        FROM call_quality_assessment
        WHERE ClientId = :client_id  
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        AND (
            LOWER(sensetive_word) LIKE '%social%'
            OR LOWER(sensetive_word) LIKE '%court%'
            OR LOWER(sensetive_word) LIKE '%consumer%'
            OR LOWER(sensetive_word) LIKE '%legal%'
            OR LOWER(sensetive_word) LIKE '%fir%'
        )
        ORDER BY DATE(CallDate) ASC;
    """)

    summary_results = db.execute(summary_query, {
        "client_id": client_id,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }).fetchall()

    raw_data_results = db.execute(raw_data_query, {
        "client_id": client_id,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }).fetchall()

    summary = [
        ComplaintSummary(
            date=row[0].strftime("%Y-%m-%d"),
            social_media_threat=row[1],
            consumer_court_threat=row[2],
            total=row[3]
        )
        for row in summary_results
    ]

    raw_data = [
        ComplaintRawData(
            date=row[0].strftime("%Y-%m-%d"),
            scenario=row[1],
            sub_scenario=row[2],
            sensitive_word=row[3]
        )
        for row in raw_data_results
    ]

    return ComplaintResponse(client_id=client_id, summary=summary, raw_data=raw_data)


@app.get("/api/negative_data_summary/")
def get_negative_data_summary(
        client_id: str = Query(..., description="Client ID"),
        db: Session = Depends(get_db2)
):
    today = date.today()
    three_months_ago = today.replace(day=1) - timedelta(days=1)
    three_months_ago = three_months_ago.replace(day=1)  # Get first day of 3 months ago
    two_days_ago = today - timedelta(days=2)

    # Query for last 3 months with monthly count
    monthly_query = text("""
        SELECT 
            DATE_FORMAT(CallDate, '%Y-%m') AS month,
            top_negative_words,
            COUNT(*) AS total_count
        FROM call_quality_assessment
        WHERE ClientId = :client_id  
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        AND (
            LOWER(top_negative_words) LIKE '%abuse%'
            OR LOWER(top_negative_words) LIKE '%threat%'
            OR LOWER(top_negative_words) LIKE '%frustration%'
            OR LOWER(top_negative_words) LIKE '%slang%'
            OR LOWER(top_negative_words) LIKE '%sarcasm%'
        )
        GROUP BY top_negative_words,DATE_FORMAT(CallDate, '%Y-%m')
        ORDER BY month ASC
    """)

    # Query for last 2 days with daily count
    daily_query = text("""
        SELECT 
            DATE(CallDate) AS date,
            top_negative_words,
            COUNT(*) AS total_count
        FROM call_quality_assessment
        WHERE ClientId = :client_id  
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        AND (
            LOWER(top_negative_words) LIKE '%abuse%'
            OR LOWER(top_negative_words) LIKE '%threat%'
            OR LOWER(top_negative_words) LIKE '%frustration%'
            OR LOWER(top_negative_words) LIKE '%slang%'
            OR LOWER(top_negative_words) LIKE '%sarcasm%'
        )
        GROUP BY top_negative_words,DATE(CallDate)
        ORDER BY date ASC
    """)

    # Execute queries
    monthly_result = db.execute(monthly_query, {
        "client_id": client_id,
        "start_date": three_months_ago,
        "end_date": today
    }).fetchall()

    daily_result = db.execute(daily_query, {
        "client_id": client_id,
        "start_date": two_days_ago,
        "end_date": today
    }).fetchall()

    # Formatting output
    monthly_data = [{"month": row[0], "negative_word": row[1], "total_count": row[2]} for row in monthly_result]
    daily_data = [{"date": row[0], "negative_word": row[1], "total_count": row[2]} for row in daily_result]

    return {
        "last_3_months": monthly_data,
        "last_2_days": daily_data
    }


@app.get("/api/competitor_data/")
def get_competitor_data(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text("""
        SELECT
            Competitor_Name,
            COUNT(*) AS total_count
        FROM call_quality_assessment
        WHERE ClientId = :client_id  
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        and Competitor_Name not in ('Not Applicable','Not Mentioned','','Not Available','N/A','NA','Not provided')
        GROUP BY Competitor_Name
    """)

    result = db.execute(query, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchall()

    return [
        {
            "Competitor_Name": row[0],
            "Count": row[1]
        }
        for row in result
    ]


####################  Fatal Details##############################

@app.get("/api/fatal_count")
def get_fatal_count(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text("""
    SELECT
        COUNT(lead_id) AS audit_cnt,
        ROUND(
            SUM(CASE WHEN scenario2 <> 'Blank Call' THEN quality_percentage ELSE 0 END) /
            NULLIF(COUNT(CASE WHEN scenario2 <> 'Blank Call' THEN lead_id END), 0),
            2
        ) AS cq_score,
        SUM(CASE WHEN professionalism_maintained = 0 AND scenario2 <> 'Blank Call' THEN 1 ELSE 0 END) AS fatal_count,
        ROUND(SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) * 100, 2) AS fatal_percentage,
        SUM(CASE WHEN scenario = 'Query' AND professionalism_maintained = 0 THEN 1 ELSE 0 END) AS query_fatal,
        SUM(CASE WHEN scenario = 'Complaint' AND professionalism_maintained = 0 THEN 1 ELSE 0 END) AS Complaint_fatal,
        SUM(CASE WHEN scenario = 'Request' AND professionalism_maintained = 0 THEN 1 ELSE 0 END) AS Request_fatal,
        SUM(CASE WHEN scenario = 'Sale Done' AND professionalism_maintained = 0 THEN 1 ELSE 0 END) AS sale_fatal
    FROM call_quality_assessment 
    WHERE ClientId = :client_id  
    AND DATE(CallDate) BETWEEN :start_date AND :end_date
    """)

    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchone()
    # print(result)
    # Handle None case to avoid errors
    if not result:
        return {"audit_cnt": 0, "cq_score": 0, "fatal_count": 0, "fatal_percentage": 0, "query_fatal": 0,
                "Complaint_fatal": 0, "Request_fatal": 0, "sale_fatal": 0}

    return {
        "audit_cnt": result[0] or 0,
        "cq_score": result[1] or 0.0,
        "fatal_count": result[2] or 0,
        "fatal_percentage": result[3] or 0,
        "query_fatal": result[4] or 0,
        "Complaint_fatal": result[5] or 0,
        "Request_fatal": result[6] or 0,
        "sale_fatal": result[7] or 0
    }


@app.get("/api/top_agents_fatal_summary")
def get_top_agents_fatal_summary(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        limit: int = Query(5, description="Number of top agents to fetch (default: 5)"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text("""
        SELECT 
            User as Agent_Name,
            COUNT(*) AS audit_count,
            SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) AS fatal_count,
            ROUND((SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0), 2) AS fatal_percentage
        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        GROUP BY Agent_Name
        ORDER BY fatal_count DESC
        LIMIT :limit;
    """)

    result = db.execute(query, {
        "client_id": client_id,  # ? FIXED: Matched query param name
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit
    }).fetchall()

    response_data = [
        {
            "Agent Name": row[0],
            "Audit Count": row[1] or 0,
            "Fatal Count": row[2] or 0,
            "Fatal%": f"{row[3] or 0}%"
        }
        for row in result
    ]

    return response_data


@app.get("/api/daywise_fatal_summary")
def get_daywise_fatal_summary(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text("""
        SELECT 
            date(CallDate) as CallDate,
            SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) AS fatal_count
        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        GROUP BY DATE(CallDate);
    """)

    result = db.execute(query, {
        "client_id": client_id,  # ? FIXED: Matched query param name
        "start_date": start_date,
        "end_date": end_date

    }).fetchall()

    response_data = [
        {
            "CallDate": row[0],
            "Fatal Count": row[1] or 0
        }
        for row in result
    ]

    return response_data


@app.get("/api/agent_audit_summary")
def get_agent_audit_summary(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text("""
        SELECT 
            User as Agent_Name,
            COUNT(*) AS audit_count,
            ROUND(AVG(quality_percentage), 2) AS cq_score_percentage,
            SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) AS fatal_count,
            ROUND((SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0), 2) AS fatal_percentage,
            ROUND((SUM(CASE WHEN quality_percentage < 50 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0), 2) AS below_average_percentage,
            ROUND((SUM(CASE WHEN quality_percentage BETWEEN 50 AND 69 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0), 2) AS average_percentage,
            ROUND((SUM(CASE WHEN quality_percentage BETWEEN 70 AND 89 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0), 2) AS good_percentage,
            ROUND((SUM(CASE WHEN quality_percentage >= 90 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0), 2) AS excellent_percentage
        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        GROUP BY Agent_Name
        ORDER BY audit_count DESC;
    """)

    result = db.execute(query, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchall()

    response_data = []
    total_audit_count = 0
    total_fatal_count = 0
    total_cq_score = 0
    total_below_avg = 0
    total_avg = 0
    total_good = 0
    total_excellent = 0

    for row in result:
        response_data.append({
            "Agent Name": row[0],
            "Audit Count": row[1] or 0,
            "CQ Score%": f"{row[2] or 0}%",
            "Fatal Count": row[3] or 0,
            "Fatal%": f"{row[4] or 0}%",
            "Below Average Calls": f"{row[5] or 0}%",
            "Average Calls": f"{row[6] or 0}%",
            "Good Calls": f"{row[7] or 0}%",
            "Excellent Calls": f"{row[8] or 0}%"
        })

        # Summing up for Grand Total
        total_audit_count += row[1] or 0
        total_fatal_count += row[3] or 0
        total_cq_score += row[2] or 0
        total_below_avg += row[5] or 0
        total_avg += row[6] or 0
        total_good += row[7] or 0
        total_excellent += row[8] or 0

    # Adding Grand Total
    if total_audit_count > 0:
        response_data.append({
            "Agent Name": "Grand Total",
            "Audit Count": total_audit_count,
            "CQ Score%": f"{round(total_cq_score / len(result), 2)}%" if result else "0%",
            "Fatal Count": total_fatal_count,
            "Fatal%": f"{round((total_fatal_count * 100) / total_audit_count, 2)}%" if total_audit_count else "0%",
            "Below Average Calls": f"{round(total_below_avg / len(result), 2)}%" if result else "0%",
            "Average Calls": f"{round(total_avg / len(result), 2)}%" if result else "0%",
            "Good Calls": f"{round(total_good / len(result), 2)}%" if result else "0%",
            "Excellent Calls": f"{round(total_excellent / len(result), 2)}%" if result else "0%"
        })

    return response_data


##################   Detailed Analysis##########################
@app.get("/api/details_count")
def get_details_count(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text("""
    SELECT
        COUNT(lead_id) AS audit_cnt,
        ROUND(
            SUM(CASE WHEN scenario2 <> 'Blank Call' THEN quality_percentage ELSE 0 END) /
            NULLIF(COUNT(CASE WHEN scenario2 <> 'Blank Call' THEN lead_id END), 0),
            2
        ) AS cq_score,
        SUM(CASE WHEN professionalism_maintained = 0 AND scenario2 <> 'Blank Call' THEN 1 ELSE 0 END) AS fatal_count,
        ROUND(SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) * 100, 2) AS fatal_percentage,
        SUM(CASE WHEN scenario = 'Query' THEN 1 ELSE 0 END) AS query_fatal,
        SUM(CASE WHEN scenario = 'Complaint' THEN 1 ELSE 0 END) AS Complaint_fatal,
        SUM(CASE WHEN scenario = 'Request' THEN 1 ELSE 0 END) AS Request_fatal,
        SUM(CASE WHEN scenario = 'Sale Done' THEN 1 ELSE 0 END) AS sale_fatal
    FROM call_quality_assessment 
    WHERE ClientId = :client_id  
    AND DATE(CallDate) BETWEEN :start_date AND :end_date
    """)

    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchone()
    # print(result)
    # Handle None case to avoid errors
    if not result:
        return {"audit_cnt": 0, "cq_score": 0, "fatal_count": 0, "fatal_percentage": 0, "query": 0, "Complaint": 0,
                "Request": 0, "sale": 0}

    return {
        "audit_cnt": result[0] or 0,
        "cq_score": result[1] or 0.0,
        "fatal_count": result[2] or 0,
        "fatal_percentage": result[3] or 0,
        "query": result[4] or 0,
        "Complaint": result[5] or 0,
        "Request": result[6] or 0,
        "sale": result[7] or 0
    }


@app.get("/api/top_scenarios_with_counts")
def get_top_scenarios_with_counts(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        limit: int = Query(5, description="Number of top reasons to fetch per category (default: 5)"),

        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    scenarios = ["Query", "Complaint", "Request"]
    response_data = {}

    for scenario in scenarios:
        query = text(f"""
            SELECT 
                scenario1 AS reason,
                COUNT(*) AS count
            FROM call_quality_assessment
            WHERE ClientId = :client_id
            AND scenario = :scenario
            AND DATE(CallDate) BETWEEN :start_date AND :end_date
            GROUP BY scenario1
            ORDER BY count DESC
            LIMIT :limit;
        """)

        result = db.execute(query, {
            "client_id": client_id,
            "scenario": scenario,
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit
        }).fetchall()

        response_data[scenario] = [{"Reason": row[0], "Count": row[1]} for row in result]

    return response_data


@app.get("/api/agent_performance_summary")
def get_agent_performance_summary(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text(f"""
        SELECT 
            User asAgent_Name,
            'TQ' AS performance_category,
            COUNT(*) AS audit_count,
            ROUND(AVG(quality_percentage), 2) AS cq_score,
            SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) AS fatal_count,
            ROUND((SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0), 2) AS fatal_percentage,

            ROUND(AVG( 
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    WHEN customer_concern_acknowledged = TRUE THEN 1
                    ELSE 0
                END
            ), 2) AS opening_score,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    ELSE 
                        (IF(professionalism_maintained = TRUE, 0.111111, 0) +
                         IF(assurance_or_appreciation_provided = TRUE, 0.111111, 0) +
                         IF(express_empathy = TRUE, 0.111111, 0) +
                         IF(pronunciation_and_clarity = TRUE, 0.111111, 0) +
                         IF(enthusiasm_and_no_fumbling = TRUE, 0.111111, 0) +
                         IF(active_listening = TRUE, 0.111111, 0) +
                         IF(politeness_and_no_sarcasm = TRUE, 0.111111, 0) +
                         IF(proper_grammar = TRUE, 0.111111, 0) +
                         IF(accurate_issue_probing = TRUE, 0.111111, 0))
                END
            ), 2) AS soft_skills_score,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    ELSE 
                        (IF(proper_hold_procedure = TRUE, 0.5, 0) +
                         IF(proper_transfer_and_language = TRUE, 0.5, 0))
                END
            ), 2) AS hold_procedure_score,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    ELSE 
                        (IF(address_recorded_completely = TRUE, 0.5, 0) +
                         IF(correct_and_complete_information = TRUE, 0.5, 0))
                END
            ), 2) AS resolution_score,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    WHEN professionalism_maintained = TRUE THEN 1
                    ELSE 0
                END
            ), 2) AS closing_score,

            ROUND((
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        WHEN customer_concern_acknowledged = TRUE THEN 1
                        ELSE 0
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        ELSE 
                            (IF(professionalism_maintained = TRUE, 0.111111, 0) +
                             IF(assurance_or_appreciation_provided = TRUE, 0.111111, 0) +
                             IF(express_empathy = TRUE, 0.111111, 0) +
                             IF(pronunciation_and_clarity = TRUE, 0.111111, 0) +
                             IF(enthusiasm_and_no_fumbling = TRUE, 0.111111, 0) +
                             IF(active_listening = TRUE, 0.111111, 0) +
                             IF(politeness_and_no_sarcasm = TRUE, 0.111111, 0) +
                             IF(proper_grammar = TRUE, 0.111111, 0) +
                             IF(accurate_issue_probing = TRUE, 0.111111, 0))
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        ELSE 
                            (IF(proper_hold_procedure = TRUE, 0.5, 0) +
                             IF(proper_transfer_and_language = TRUE, 0.5, 0))
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        ELSE 
                            (IF(address_recorded_completely = TRUE, 0.5, 0) +
                             IF(correct_and_complete_information = TRUE, 0.5, 0))
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        WHEN professionalism_maintained = TRUE THEN 1
                        ELSE 0
                    END
                )
            ) / 5, 2) AS avg_score 

        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        GROUP BY User
        ORDER BY audit_count DESC;
    """)

    result = db.execute(query, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchall()

    response_data = []
    for row in result:
        response_data.append({
            "Agent Name": row[0],
            "TQ/MQ/BQ": row[1],
            "Audit Count": row[2],
            "CQ Score%": f"{row[3] or 0}%",
            "Fatal Count": row[4] or 0,
            "Fatal%": f"{row[5] or 0}%",
            "Opening Score%": f"{row[6] or 0}%",
            "Soft Skills Score%": f"{row[7] or 0}%",
            "Hold Procedure Score%": f"{row[8] or 0}%",
            "Resolution Score%": f"{row[9] or 0}%",
            "Closing Score%": f"{row[10] or 0}%",
            "Average Score%": f"{row[11] or 0}%"
        })

    return response_data


@app.get("/api/day_performance_summary")
def get_day_performance_summary(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text(f"""
        SELECT 
            date(CallDate) as CallDate,
            'TQ' AS performance_category,
            COUNT(*) AS audit_count,
            ROUND(AVG(quality_percentage), 2) AS cq_score,
            SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) AS fatal_count,
            ROUND((SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0), 2) AS fatal_percentage,

            ROUND(AVG( 
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    WHEN customer_concern_acknowledged = TRUE THEN 1
                    ELSE 0
                END
            ), 2) AS opening_score,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    ELSE 
                        (IF(professionalism_maintained = TRUE, 0.111111, 0) +
                         IF(assurance_or_appreciation_provided = TRUE, 0.111111, 0) +
                         IF(express_empathy = TRUE, 0.111111, 0) +
                         IF(pronunciation_and_clarity = TRUE, 0.111111, 0) +
                         IF(enthusiasm_and_no_fumbling = TRUE, 0.111111, 0) +
                         IF(active_listening = TRUE, 0.111111, 0) +
                         IF(politeness_and_no_sarcasm = TRUE, 0.111111, 0) +
                         IF(proper_grammar = TRUE, 0.111111, 0) +
                         IF(accurate_issue_probing = TRUE, 0.111111, 0))
                END
            ), 2) AS soft_skills_score,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    ELSE 
                        (IF(proper_hold_procedure = TRUE, 0.5, 0) +
                         IF(proper_transfer_and_language = TRUE, 0.5, 0))
                END
            ), 2) AS hold_procedure_score,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    ELSE 
                        (IF(address_recorded_completely = TRUE, 0.5, 0) +
                         IF(correct_and_complete_information = TRUE, 0.5, 0))
                END
            ), 2) AS resolution_score,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    WHEN professionalism_maintained = TRUE THEN 1
                    ELSE 0
                END
            ), 2) AS closing_score,

            ROUND((
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        WHEN customer_concern_acknowledged = TRUE THEN 1
                        ELSE 0
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        ELSE 
                            (IF(professionalism_maintained = TRUE, 0.111111, 0) +
                             IF(assurance_or_appreciation_provided = TRUE, 0.111111, 0) +
                             IF(express_empathy = TRUE, 0.111111, 0) +
                             IF(pronunciation_and_clarity = TRUE, 0.111111, 0) +
                             IF(enthusiasm_and_no_fumbling = TRUE, 0.111111, 0) +
                             IF(active_listening = TRUE, 0.111111, 0) +
                             IF(politeness_and_no_sarcasm = TRUE, 0.111111, 0) +
                             IF(proper_grammar = TRUE, 0.111111, 0) +
                             IF(accurate_issue_probing = TRUE, 0.111111, 0))
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        ELSE 
                            (IF(proper_hold_procedure = TRUE, 0.5, 0) +
                             IF(proper_transfer_and_language = TRUE, 0.5, 0))
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        ELSE 
                            (IF(address_recorded_completely = TRUE, 0.5, 0) +
                             IF(correct_and_complete_information = TRUE, 0.5, 0))
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        WHEN professionalism_maintained = TRUE THEN 1
                        ELSE 0
                    END
                )
            ) / 5, 2) AS avg_score 

        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        GROUP BY DATE(CallDate)
        ORDER BY audit_count DESC;
    """)

    result = db.execute(query, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchall()

    response_data = []
    for row in result:
        response_data.append({
            "Call Date": row[0],
            "TQ/MQ/BQ": row[1],
            "Audit Count": row[2],
            "CQ Score%": f"{row[3] or 0}%",
            "Fatal Count": row[4] or 0,
            "Fatal%": f"{row[5] or 0}%",
            "Opening Score%": f"{row[6] or 0}%",
            "Soft Skills Score%": f"{row[7] or 0}%",
            "Hold Procedure Score%": f"{row[8] or 0}%",
            "Resolution Score%": f"{row[9] or 0}%",
            "Closing Score%": f"{row[10] or 0}%",
            "Average Score%": f"{row[11] or 0}%"
        })

    return response_data


######################### Week wise ####################
@app.get("/api/week_performance_summary")
def get_week_performance_summary(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    query = text(f"""
        SELECT 
            YEAR(CallDate) AS year,
            WEEK(CallDate, 1) AS week_number,  -- ISO Week starts on Monday
            COUNT(*) AS audit_count,
            ROUND(AVG(quality_percentage), 2) AS cq_score,
            SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) AS fatal_count,
            ROUND((SUM(CASE WHEN professionalism_maintained = 0 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0), 2) AS fatal_percentage,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    WHEN customer_concern_acknowledged = TRUE THEN 1
                    ELSE 0
                END
            ), 2) AS opening_score,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    ELSE 
                        (IF(professionalism_maintained = TRUE, 0.111111, 0) +
                         IF(assurance_or_appreciation_provided = TRUE, 0.111111, 0) +
                         IF(express_empathy = TRUE, 0.111111, 0) +
                         IF(pronunciation_and_clarity = TRUE, 0.111111, 0) +
                         IF(enthusiasm_and_no_fumbling = TRUE, 0.111111, 0) +
                         IF(active_listening = TRUE, 0.111111, 0) +
                         IF(politeness_and_no_sarcasm = TRUE, 0.111111, 0) +
                         IF(proper_grammar = TRUE, 0.111111, 0) +
                         IF(accurate_issue_probing = TRUE, 0.111111, 0))
                END
            ), 2) AS soft_skills_score,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    ELSE 
                        (IF(proper_hold_procedure = TRUE, 0.5, 0) +
                         IF(proper_transfer_and_language = TRUE, 0.5, 0))
                END
            ), 2) AS hold_procedure_score,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    ELSE 
                        (IF(address_recorded_completely = TRUE, 0.5, 0) +
                         IF(correct_and_complete_information = TRUE, 0.5, 0))
                END
            ), 2) AS resolution_score,

            ROUND(AVG(
                CASE 
                    WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                    WHEN professionalism_maintained = TRUE THEN 1
                    ELSE 0
                END
            ), 2) AS closing_score,

            ROUND((AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        WHEN customer_concern_acknowledged = TRUE THEN 1
                        ELSE 0
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        ELSE 
                            (IF(professionalism_maintained = TRUE, 0.111111, 0) +
                             IF(assurance_or_appreciation_provided = TRUE, 0.111111, 0) +
                             IF(express_empathy = TRUE, 0.111111, 0) +
                             IF(pronunciation_and_clarity = TRUE, 0.111111, 0) +
                             IF(enthusiasm_and_no_fumbling = TRUE, 0.111111, 0) +
                             IF(active_listening = TRUE, 0.111111, 0) +
                             IF(politeness_and_no_sarcasm = TRUE, 0.111111, 0) +
                             IF(proper_grammar = TRUE, 0.111111, 0) +
                             IF(accurate_issue_probing = TRUE, 0.111111, 0))
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        ELSE 
                            (IF(proper_hold_procedure = TRUE, 0.5, 0) +
                             IF(proper_transfer_and_language = TRUE, 0.5, 0))
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        ELSE 
                            (IF(address_recorded_completely = TRUE, 0.5, 0) +
                             IF(correct_and_complete_information = TRUE, 0.5, 0))
                    END
                ) +
                AVG(
                    CASE 
                        WHEN scenario1 IN ('Call Drop in between', 'Short Call/Blank Call') THEN 1
                        WHEN professionalism_maintained = TRUE THEN 1
                        ELSE 0
                    END
                )
            ) / 5, 2) AS avg_score 

        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        GROUP BY year, week_number
        ORDER BY year DESC, week_number DESC;
    """)

    result = db.execute(query, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchall()

    response_data = []
    for row in result:
        response_data.append({
            "Year": row[0],
            "Week Number": row[1],
            "Audit Count": row[2],
            "CQ Score%": f"{row[3] or 0}%",
            "Fatal Count": row[4] or 0,
            "Fatal%": f"{row[5] or 0}%",
            "Opening Score%": f"{row[6] or 0}%",
            "Soft Skills Score%": f"{row[7] or 0}%",
            "Hold Procedure Score%": f"{row[8] or 0}%",
            "Resolution Score%": f"{row[9] or 0}%",
            "Closing Score%": f"{row[10] or 0}%",
            "Average Score%": f"{row[11] or 0}%"
        })

    return response_data


###############  Search Lead##########################
class CallQualityAssessment(BaseModel):
    client_id: str
    mobile_no: str
    user: str
    lead_id: str
    call_date: str  # Convert date to string format
    customer_concern_acknowledged: Optional[int]
    professionalism_maintained: Optional[int]
    assurance_or_appreciation_provided: Optional[int]
    pronunciation_and_clarity: Optional[int]
    enthusiasm_and_no_fumbling: Optional[int]
    active_listening: Optional[int]
    politeness_and_no_sarcasm: Optional[int]
    proper_grammar: Optional[int]
    accurate_issue_probing: Optional[int]
    proper_hold_procedure: Optional[int]
    proper_transfer_and_language: Optional[int]
    address_recorded_completely: Optional[int]
    correct_and_complete_information: Optional[int]
    proper_call_closure: Optional[int]
    express_empathy: Optional[int]
    total_score: Optional[int]
    max_score: Optional[int]
    quality_percentage: Optional[float]
    areas_for_improvement: Optional[str]
    transcribe_text: Optional[str]


# ? Define API inside APIRouter
@app.get("/api/call_quality_details/", response_model=CallQualityAssessment)
def get_call_quality_details(
        client_id: str = Query(..., description="Client ID"),
        lead_id: str = Query(..., description="Lead ID"),
        db: Session = Depends(get_db2)
):
    query = text("""
        SELECT 
            ClientId, MobileNo, User, lead_id, CallDate, 
            customer_concern_acknowledged, professionalism_maintained, 
            assurance_or_appreciation_provided, pronunciation_and_clarity, 
            enthusiasm_and_no_fumbling, active_listening, 
            politeness_and_no_sarcasm, proper_grammar, accurate_issue_probing, 
            proper_hold_procedure, proper_transfer_and_language, 
            address_recorded_completely, correct_and_complete_information, 
            proper_call_closure, express_empathy, total_score, 
            max_score, quality_percentage, areas_for_improvement, 
            Transcribe_Text
        FROM call_quality_assessment
        WHERE ClientId = :client_id AND lead_id = :lead_id
    """)

    result = db.execute(query, {"client_id": client_id, "lead_id": lead_id}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="No data found for the given Client ID and Lead ID")

    return CallQualityAssessment(
        client_id=result[0],
        mobile_no=result[1],
        user=result[2],
        lead_id=result[3],
        call_date=result[4].strftime("%Y-%m-%d"),  # ? Convert date to string
        customer_concern_acknowledged=result[5],
        professionalism_maintained=result[6],
        assurance_or_appreciation_provided=result[7],
        pronunciation_and_clarity=result[8],
        enthusiasm_and_no_fumbling=result[9],
        active_listening=result[10],
        politeness_and_no_sarcasm=result[11],
        proper_grammar=result[12],
        accurate_issue_probing=result[13],
        proper_hold_procedure=result[14],
        proper_transfer_and_language=result[15],
        address_recorded_completely=result[16],
        correct_and_complete_information=result[17],
        proper_call_closure=result[18],
        express_empathy=result[19],
        total_score=result[20],
        max_score=result[21],
        quality_percentage=result[22],
        areas_for_improvement=result[23],
        transcribe_text=result[24]
    )


##################  Raw Dump ####################################
@app.get("/api/call_quality_assessments")
def get_call_quality_assessments(
        client_id: str = Query(..., description="Client ID"),
        start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
        end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    query = text("""
        SELECT * 
        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
    """)

    result = db.execute(query, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchall()

    # Convert result to JSON-friendly format
    response_data = [dict(row._mapping) for row in result]

    return response_data


#######  Potential Scam###################

@app.get("/api/potential_data_summarry")
def get_potential_data_summarry(
        client_id: str = Query(..., description="Client ID"),
        start_date: date = Query(None, description="Start Date in YYYY-MM-DD format"),
        end_date: date = Query(None, description="End Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db2)
):
    # Use current date if start_date or end_date is not provided
    today = date.today()
    start_date = start_date or today
    end_date = end_date or today
    # Query to get the summarized count
    query_counts = text("""
        SELECT 
            SUM(CASE WHEN LOWER(sensetive_word) LIKE '%social%' THEN 1 ELSE 0 END) AS social_media_threat,
            SUM(CASE WHEN LOWER(sensetive_word) LIKE '%court%'
                        OR LOWER(sensetive_word) LIKE '%consumer%'
                        OR LOWER(sensetive_word) LIKE '%legal%'
                        OR LOWER(sensetive_word) LIKE '%fir%' THEN 1 ELSE 0 END) AS consumer_court_threat,
            SUM(CASE WHEN system_manipulation = 'Yes' THEN 1 ELSE 0 END) AS potential_scam,
            SUM(CASE WHEN LOWER(top_negative_words) LIKE '%abuse%' THEN 1 ELSE 0 END) AS abuse,
            SUM(CASE WHEN LOWER(top_negative_words) LIKE '%threat%' THEN 1 ELSE 0 END) AS threat,
            SUM(CASE WHEN LOWER(top_negative_words) LIKE '%frustration%' THEN 1 ELSE 0 END) AS frustration,
            SUM(CASE WHEN LOWER(top_negative_words) LIKE '%slang%' THEN 1 ELSE 0 END) AS slang,
            SUM(CASE WHEN LOWER(top_negative_words) LIKE '%sarcasm%' THEN 1 ELSE 0 END) AS sarcasm
        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
    """)

    count_result = db.execute(query_counts, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchone()

    # Convert count result to dictionary
    count_data = dict(count_result._mapping)

    # Query to get raw dump
    query_raw_dump = text("""
        SELECT *
        FROM call_quality_assessment
        WHERE ClientId = :client_id
        AND (LOWER(sensetive_word) LIKE '%social%'
             OR LOWER(sensetive_word) LIKE '%court%'
             OR LOWER(sensetive_word) LIKE '%consumer%'
             OR LOWER(sensetive_word) LIKE '%legal%'
             OR LOWER(sensetive_word) LIKE '%fir%'
             OR system_manipulation = 'Yes'
             OR LOWER(top_negative_words) LIKE '%abuse%'
             OR LOWER(top_negative_words) LIKE '%threat%'
             OR LOWER(top_negative_words) LIKE '%frustration%'
             OR LOWER(top_negative_words) LIKE '%slang%'
             OR LOWER(top_negative_words) LIKE '%sarcasm%')
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
    """)

    raw_dump_result = db.execute(query_raw_dump, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchall()

    # Convert raw dump result to JSON-friendly format
    raw_dump_data = [dict(row._mapping) for row in raw_dump_result]

    return {
        "counts": count_data,
        "raw_dump": raw_dump_data
    }


################### API Key ############################


# Get all API keys
@app.get("/api/get-keys")
def get_keys(db: Session = Depends(get_db)):
    keys = db.query(APIKey).all()
    return [{"api_key": key.api_key, "created_at": key.created_at, "status": key.status} for key in keys]


@app.get("/api/recordings/")
def get_recordings(user_id: int = Query(...), db: Session = Depends(get_db)):
    recordings = db.query(AudioFile).filter(AudioFile.user_id == user_id).all()
    response_data = [
        {
            "preview": "??",
            "recordingDate": rec.upload_time.strftime("%Y-%m-%d"),
            "file": rec.filename,
            "category": rec.category if rec.category else "Unknown",
            "language": rec.language if rec.language else "NA",
            "minutes": rec.minutes if rec.minutes else "NA",
            "Transcript": rec.transcript if rec.transcript else "NA",
            "id": rec.id,
            "user_id": rec.user_id
        }
        for rec in recordings
    ]
    return response_data


@app.get("/api/recordings_datewise/")

def get_recordings_datewise(
    start_date: str = Query(None, description="Start Date in YYYY-MM-DD format"),
    end_date: str = Query(None, description="End Date in YYYY-MM-DD format"),
    user_id: int = Query(..., description="User ID to filter recordings"),
    db: Session = Depends(get_db),
):
    query = db.query(AudioFile)
    from datetime import datetime, date, timedelta
    # Default to today's date if none provided
    today = date.today()
    start_date = start_date or today.strftime("%Y-%m-%d")
    end_date = end_date or today.strftime("%Y-%m-%d")

    try:

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="start_date cannot be after end_date")

        query = query.filter(
            AudioFile.upload_time >= start_dt,
            AudioFile.upload_time <= end_dt,
            AudioFile.user_id == user_id  # Filter by user ID
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    recordings = query.all()

    response_data = [
        {
            "preview": "??",
            "recordingDate": rec.upload_time.strftime("%Y-%m-%d"),
            "file": rec.filename,
            "category": rec.category or "Unknown",
            "language": rec.language or "NA",
            "minutes": rec.minutes or "NA",
            "Transcript": rec.transcript or "NA",
            "id": rec.id,
            "user_id": rec.user_id
        }
        for rec in recordings
    ]

    return response_data


UPLOAD_DIR_NEW = "downloaded_files"  # Directory to store text files
os.makedirs(UPLOAD_DIR_NEW, exist_ok=True)  # Ensure directory exists
from fastapi.responses import FileResponse


@app.post("/api/download_transcription/")
async def download_transcription(data: dict, db: Session = Depends(get_db)):
    ids = data.get("ids", [])
    if not ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    # Fetch matching records from the database
    audio_records = db.query(AudioFile).filter(AudioFile.id.in_(ids)).all()
    if not audio_records:
        raise HTTPException(status_code=404, detail="No matching records found")

    # Generate transcription text
    text_content = "\n\n".join(
        [f"ID: {audio.id}\nFilename: {audio.filename}\nCategory: {audio.category}\nTranscript: {audio.transcript}"
         for audio in audio_records]
    )

    # Save text file
    file_path = os.path.join(UPLOAD_DIR_NEW, "transcriptions.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text_content)

    # Return file for download
    return FileResponse(file_path, filename="transcriptions.txt", media_type="text/plain")


@app.get("/api/calculate_limit/")
async def calculate_limit(user_id: int, db: Session = Depends(get_db)):
    user_minutes = db.query(AudioFile.minutes).filter(AudioFile.user_id == user_id).all()

    if not user_minutes:
        return {"user_id": user_id, "total_minutes": "00.00"}

    total_seconds = 0

    for (minute_value,) in user_minutes:
        if minute_value is not None:
            minutes_part = int(minute_value)
            seconds_part = round((minute_value - minutes_part) * 100)
            total_seconds += (minutes_part * 60) + seconds_part

    total_minutes = total_seconds // 60
    total_remaining_seconds = total_seconds % 60

    formatted_total = f"{total_minutes}.{str(total_remaining_seconds).zfill(2)}"

    return {"user_id": user_id, "total_minutes": formatted_total}


class LimitRequest(BaseModel):
    from_date: date
    to_date: date
    user_id: int


@app.post("/api/calculate_limit_date/")
async def calculate_limit_date(request: LimitRequest, db: Session = Depends(get_db)):
    user_minutes = (
        db.query(AudioFile.minutes)
        .filter(
            AudioFile.user_id == request.user_id,
            func.date(AudioFile.upload_time).between(request.from_date, request.to_date)
        )
        .all()
    )

    if not user_minutes:
        return {
            "user_id": request.user_id,
            "from_date": str(request.from_date),
            "to_date": str(request.to_date),
            "total_minutes": "00.00"
        }

    total_seconds = 0
    for (minute_value,) in user_minutes:
        if minute_value is not None:
            minutes_part = int(minute_value)
            seconds_part = round((minute_value - minutes_part) * 100)
            total_seconds += (minutes_part * 60) + seconds_part

    total_minutes = total_seconds // 60
    total_remaining_seconds = total_seconds % 60
    formatted_total = f"{total_minutes}.{str(total_remaining_seconds).zfill(2)}"

    return {
        "user_id": request.user_id,
        "from_date": str(request.from_date),
        "to_date": str(request.to_date),
        "total_minutes": formatted_total
    }


@app.get("/api/menu")
def fetch_menu(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            m1.id AS main_id, 
            m1.page_name AS main_name, 
            m1.page_icon AS main_icon, 
            m1.page_url AS main_url, 
            m2.id AS submenu_id, 
            m2.page_name AS submenu_name, 
            m2.page_icon AS submenu_icon, 
            m2.page_url AS submenu_url
        FROM menu_master m1
        LEFT JOIN menu_master m2 ON m1.id = m2.parent_id
        ORDER BY m1.id, m2.id;
    """)

    result = db.execute(query).fetchall()

    menu_dict = {}

    for row in result:
        main_id = row.main_id

        if main_id not in menu_dict:
            menu_dict[main_id] = {
                "id": main_id,
                "name": row.main_name,
                "icon": row.main_icon,
                "url": row.main_url,
                "submenu": []
            }

        if row.submenu_id:
            menu_dict[main_id]["submenu"].append({
                "id": row.submenu_id,
                "name": row.submenu_name,
                "icon": row.submenu_icon,
                "url": row.submenu_url
            })

    return list(menu_dict.values())


#############################################  Sales #############################

@app.get("/api/call_summary_sales")
def get_call_summary_sales(
        client_id: str = Query(..., description="Client ID"),
        start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
        end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
        db: Session = Depends(get_db3)
):
    query_summary = text("""
        SELECT
            COUNT(DISTINCT id) AS total_calls,
            COUNT(DISTINCT CASE WHEN OpeningRejected = 0 THEN id END) AS exclude_opening_rejected,
            COUNT(DISTINCT CASE WHEN OpeningRejected = 0 AND ContactSettingContext IS NULL THEN id END) AS exclude_context_opening_rejected,
            COUNT(DISTINCT CASE WHEN OpeningRejected = 0 AND ContactSettingContext IS NULL AND OfferingRejected = 0 THEN id END) AS exclude_context_opening_offering_rejected,
            COUNT(DISTINCT CASE WHEN SaleDone = 1 THEN id END) AS sale_done_count,
            ROUND((COUNT(DISTINCT CASE WHEN SaleDone = 1 THEN id END) / COUNT(DISTINCT id)) * 100, 2) AS sale_success_rate,
            COUNT(DISTINCT CASE WHEN OpeningRejected = 1 THEN id END) AS include_opening_rejected,
            COUNT(DISTINCT CASE WHEN ContactSettingContext IS NOT NULL THEN id END) AS include_context_rejected,
            COUNT(DISTINCT CASE WHEN OfferingRejected = 1 THEN id END) AS offering_rejected_count,
            COUNT(DISTINCT CASE WHEN AfterListeningOfferRejected = 1 THEN id END) AS post_offer_rejected_count,
            ROUND(((COUNT(DISTINCT id) - COUNT(DISTINCT CASE WHEN SaleDone = 1 THEN id END)) / COUNT(DISTINCT id)) * 100, 2) AS failure_rate
        FROM CallDetails
        WHERE client_id = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
    """)
    summary_result = db.execute(query_summary, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchone()
    summary_data = dict(summary_result._mapping)
    return {"call_summary": summary_data}


@app.get("/api/call_category_counts_sales")
def get_call_category_counts_sales(client_id: str = Query(..., description="Client ID"),
                                   start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
                                   end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
                                   db: Session = Depends(get_db3)):
    query = text("""
        SELECT
            COUNT(CASE WHEN AfterListeningOfferRejected = 1 THEN 1 END) AS post_offer_rejected,
            COUNT(CASE WHEN SaleDone = 1 THEN 1 END) AS sale_done,
            COUNT(CASE WHEN ObjectionHandlingContext = 'None' THEN 1 END) AS offering_rejected,
            COUNT(CASE WHEN ContactSettingContext = 'None' THEN 1 END) AS context_rejected,
            COUNT(CASE WHEN OpeningRejected = 1 THEN 1 END) AS opening_rejected,
            COUNT(CASE WHEN OfferedPitchContext = 'None' THEN 1 END) AS opening_rejected_extra
        FROM CallDetails
        WHERE client_id = :client_id AND DATE(CallDate) BETWEEN :start_date AND :end_date
    """)
    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchone()
    response_data = {
        "Post Offer Rejected": result.post_offer_rejected + result.sale_done,
        "Offering Rejected": result.offering_rejected,
        "Context Rejected": result.context_rejected,
        "Opening Rejected": result.opening_rejected + result.opening_rejected_extra
    }
    return response_data


@app.get("/api/get_call_dump_sales")
def get_call_dump_sales(
        client_id: str = Query(..., description="Client ID"),
        start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
        end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
        db: Session = Depends(get_db3)
):
    query = text("""
        SELECT * FROM CallDetails 
        WHERE client_id = :client_id 
        AND DATE(CallDate) BETWEEN :start_date AND :end_date 
        LIMIT 10
    """)

    result = db.execute(query, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchall()

    response_data = [dict(row._mapping) for row in result]
    return response_data


# Mapping of objections to categories and insights
OBJECTION_MAPPING = {
    "Already has the same product": ("No Need", "Customer already has same product; no need to buy."),
    "Already has enough perfumes": ("No Need", "Fully stocked; low chance of purchase."),
    "Overstock / No Need for More": ("No Need", "No immediate need; possible future purchase."),
    "Already Owns Enough": ("No Need", "No need for additional purchases now."),
    "Already has too many perfumes": ("No Need", "Similar to overstocked; minimal conversion potential."),
    "Already has another preferred brand": ("Brand Preference", "Prefers another brand; difficult to convert."),
    "Liked the product but wants a better deal": ("Price Sensitivity", "Possible to convert with discounts or offers."),
    "Wants to buy later": ("Budget Constraint", "Future potential lead; needs follow-up."),
    "Not Interested in Perfumes": ("Product Disinterest", "No interest at all; unlikely to convert."),
    "Happy with the product but not interested in buying more": (
    "No Need", "No further purchase intent; hard to upsell."),
    "Didn't like one of the perfumes": (
    "Negative Experience", "A bad experience with one variant; can recommend others."),
    "Disappointed with perfume quality": ("Negative Experience", "Concerns about quality; provide product assurance."),
    "Perfume Longevity Issue": (
    "Negative Experience", "Customer finds longevity lacking; suggest long-lasting alternatives."),
    "Perfume too strong": ("Negative Experience", "Scent preference issue; suggest milder alternatives."),
    "Damaged Product Received": ("Logistic Concern", "A serious issue; needs strong resolution to regain trust."),
    "Wrong Product Received": ("Logistic Concern", "Fulfillment error; needs rectification and trust-building."),
    "Doesn't trust online payments": (
    "Trust Concerns", "Major barrier; provide secure payment options and reassurance."),
}


@app.get("/api/get_mo_breakdown")
def get_mo_breakdown(client_id: str = Query(..., description="Client ID"),
                     start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
                     end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
                     db: Session = Depends(get_db3)):
    query = text("""
        SELECT CustomerObjectionSubCategory
        FROM CallDetails
        WHERE client_id = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
    """)
    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchall()
    df = pd.DataFrame(result, columns=["CustomerObjectionSubCategory"])
    total_opportunities = len(df)
    excluded_categories = {"Opening Rejected", "Context Rejected", "Offering Rejected"}
    workable_df = df[~df["CustomerObjectionSubCategory"].isin(excluded_categories)]
    mo_count = len(workable_df)
    workable_df["MO Category"] = workable_df["CustomerObjectionSubCategory"].map(
        lambda x: OBJECTION_MAPPING.get(x, ("Other", ""))[0])
    workable_df["Observations & Insights"] = workable_df["CustomerObjectionSubCategory"].map(
        lambda x: OBJECTION_MAPPING.get(x, ("", "No insight available"))[1])
    breakdown = (workable_df.groupby(["MO Category", "Observations & Insights"]).size().reset_index(name="Count"))
    breakdown["Count"] = breakdown["Count"].astype(int)
    breakdown["Contr%"] = (breakdown["Count"] / breakdown["Count"].sum() * 100).round(1).astype(float)
    mo_breakdown = breakdown.to_dict(orient="records")
    response = {
        "Total Opportunities": int(total_opportunities),
        "MO Count": int(mo_count),
        "Workable%": round((mo_count / total_opportunities) * 100, 1) if total_opportunities else 0,
        "Non Workable%": round(100 - ((mo_count / total_opportunities) * 100), 1) if total_opportunities else 0,
        "MO Breakdown": mo_breakdown,
        "Grand Total": int(breakdown["Count"].sum()),
    }
    return response


NED_ED_MAPPING = {
    "Already has the same product": ("No Need", "Already has too many perfumes", "Non Workable"),
    "Already has enough perfumes": ("No Need", "Already has too many perfumes", "Non Workable"),
    "Overstock / No Need for More": ("No Need", "Already has too many perfumes", "Non Workable"),
    "Already Owns Enough": ("No Need", "Already has too many perfumes", "Non Workable"),
    "Already has too many perfumes": ("No Need", "Already has too many perfumes", "Non Workable"),
    "Already has another preferred brand": ("Brand Preference", "Already has another preferred brand", "Non Workable"),
    "Liked the product but wants a better deal": (
    "Price Sensitivity", "Liked the product but wants a better deal", "Workable"),
    "Wants to buy later": ("Budget Constraint", "Wants to buy later", "Workable"),
    "Not Interested in Perfumes": ("Product Disinterest", "Not Interested in Perfumes", "Non Workable"),
    "Happy with the product but not interested in buying more": (
    "No Need", "Happy with the product but not interested in buying more", "Non Workable"),
    "Didn't like one of the perfumes": ("Negative Experience", "Disappointed with perfume quality", "Non Workable"),
    "Disappointed with perfume quality": ("Negative Experience", "Disappointed with perfume quality", "Non Workable"),
    "Perfume Longevity Issue": ("Negative Experience", "Perfume Longevity Issue", "Workable"),
    "Perfume too strong": ("Negative Experience", "Perfume too strong", "Workable"),
    "Damaged Product Received": ("Logistic Concern", "Damaged Product Received", "Workable"),
    "Wrong Product Received": ("Logistic Concern", "Wrong Product Received", "Workable"),
    "Doesn't trust online payments": ("Trust Concerns", "Doesn't trust online payments", "Workable"),
}


@app.get("/api/get_ned_ed_breakdown")
def get_ned_ed_breakdown(
        client_id: str = Query(..., description="Client ID"),
        start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
        end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
        db: Session = Depends(get_db3)
):
    query = text("""
        SELECT CustomerObjectionSubCategory
        FROM CallDetails
        WHERE client_id = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
    """)

    result = db.execute(query, {
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date
    }).fetchall()

    df = pd.DataFrame(result, columns=["CustomerObjectionSubCategory"])
    total_opportunities = len(df)

    df["NED/ED Category"] = df["CustomerObjectionSubCategory"].map(
        lambda x: NED_ED_MAPPING.get(x, ("Other", "", ""))[0])
    df["NED/ED-QS"] = df["CustomerObjectionSubCategory"].map(lambda x: NED_ED_MAPPING.get(x, ("", "", ""))[1])
    df["NED/ED Status"] = df["CustomerObjectionSubCategory"].map(lambda x: NED_ED_MAPPING.get(x, ("", "", ""))[2])

    breakdown = (
        df.groupby(["NED/ED Category", "NED/ED-QS", "NED/ED Status"])
        .size()
        .reset_index(name="Count")
    )

    breakdown["Count"] = breakdown["Count"].astype(int)
    breakdown["Contribution"] = (breakdown["Count"] / breakdown["Count"].sum() * 100).round(1).astype(float)

    ned_ed_breakdown = breakdown.to_dict(orient="records")

    response = {
        "Total Opportunities": int(total_opportunities),
        "NED/ED Breakdown": ned_ed_breakdown,
        "Grand Total": int(breakdown["Count"].sum()),
    }

    return response


@app.get("/api/op_analysis_sales")
def op_analysis_sales(
        client_id: str = Query(..., description="Client ID"),
        start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
        end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
        db: Session = Depends(get_db3)
):
    query = text("""
        SELECT
            OpeningPitchCategory AS "Opening Pitch Category",
            COUNT(DISTINCT LeadID) AS "Total Calls",
            SUM(CASE WHEN OpeningRejected = '1' THEN 1 ELSE 0 END) AS "OPS Count",
            ROUND((SUM(CASE WHEN OpeningRejected = '1' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)), 2) AS "OPS%",
            SUM(CASE WHEN OpeningRejected = '0' THEN 1 ELSE 0 END) AS "OR Count",
            ROUND((SUM(CASE WHEN OpeningRejected = '0' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)), 2) AS "OR%",
            SUM(CASE WHEN SaleDone = TRUE THEN 1 ELSE 0 END) AS "Sale Count",
            ROUND((SUM(CASE WHEN SaleDone = TRUE THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)), 2) AS "Conversion%"
        FROM CallDetails
        WHERE client_id = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        GROUP BY OpeningPitchCategory
        ORDER BY "Total Calls" DESC
    """)

    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchall()
    response_data = [dict(row._mapping) for row in result]

    if response_data:
        total_calls = sum(row["Total Calls"] for row in response_data)
        ops_count = sum(row["OPS Count"] for row in response_data)
        or_count = sum(row["OR Count"] for row in response_data)
        sale_count = sum(row["Sale Count"] for row in response_data)

        grand_total = {
            "Opening Pitch Category": "Grand Total",
            "Total Calls": total_calls,
            "OPS Count": ops_count,
            "OPS%": round(float(ops_count) * 100.0 / max(float(total_calls), 1.0), 2),
            "OR Count": or_count,
            "OR%": round(float(or_count) * 100.0 / max(float(total_calls), 1.0), 2),
            "Sale Count": sale_count,
            "Conversion%": round(float(sale_count) * 100.0 / max(float(total_calls), 1.0), 2)
        }

        response_data.append(grand_total)

    return response_data


@app.get("/api/contact_analysis_sales")
def contact_analysis_sales(
        client_id: str = Query(..., description="Client ID"),
        start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
        end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
        db: Session = Depends(get_db3)
):
    query = text("""
        SELECT
            ContactSettingCategory AS "Contact Pitch Category",
            COUNT(DISTINCT LeadID) AS "Total Calls",
            SUM(CASE WHEN OpeningRejected = '1' THEN 1 ELSE 0 END) AS "OPS Count",
            ROUND((SUM(CASE WHEN OpeningRejected = '1' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)), 2) AS "OPS%",
            SUM(CASE WHEN OpeningRejected = '0' THEN 1 ELSE 0 END) AS "OR Count",
            ROUND((SUM(CASE WHEN OpeningRejected = '0' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)), 2) AS "OR%",
            SUM(CASE WHEN SaleDone = TRUE THEN 1 ELSE 0 END) AS "Sale Count",
            ROUND((SUM(CASE WHEN SaleDone = TRUE THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)), 2) AS "Conversion%"
        FROM CallDetails
        WHERE client_id = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        GROUP BY ContactSettingCategory
        ORDER BY "Total Calls" DESC
    """)

    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchall()
    response_data = [dict(row._mapping) for row in result]

    if response_data:
        total_calls = sum(row["Total Calls"] for row in response_data)
        ops_count = sum(row["OPS Count"] for row in response_data)
        or_count = sum(row["OR Count"] for row in response_data)
        sale_count = sum(row["Sale Count"] for row in response_data)

        grand_total = {
            "Contact Pitch Category": "Grand Total",
            "Total Calls": int(total_calls),
            "OPS Count": int(ops_count),
            "OPS%": round(float(ops_count) * 100.0 / max(float(total_calls), 1.0), 2),
            "OR Count": int(or_count),
            "OR%": round(float(or_count) * 100.0 / max(float(total_calls), 1.0), 2),
            "Sale Count": int(sale_count),
            "Conversion%": round(float(sale_count) * 100.0 / max(float(total_calls), 1.0), 2)
        }

        response_data.append(grand_total)

    return response_data


@app.get("/api/discount_analysis_sales")
def discount_analysis_sales(
        client_id: str = Query(..., description="Client ID"),
        start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
        end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
        db: Session = Depends(get_db3)
):
    query = text("""
        SELECT
            DiscountType AS "Discount Type",
            COUNT(DISTINCT LeadID) AS "Total Calls",
            SUM(CASE WHEN OpeningRejected = '1' THEN 1 ELSE 0 END) AS "OPS Count",
            ROUND((SUM(CASE WHEN OpeningRejected = '1' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)), 2) AS "OPS%",
            SUM(CASE WHEN OpeningRejected = '0' THEN 1 ELSE 0 END) AS "OR Count",
            ROUND((SUM(CASE WHEN OpeningRejected = '0' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)), 2) AS "OR%",
            SUM(CASE WHEN SaleDone = TRUE THEN 1 ELSE 0 END) AS "Sale Count",
            ROUND((SUM(CASE WHEN SaleDone = TRUE THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)), 2) AS "Conversion%"
        FROM CallDetails
        WHERE client_id = :client_id
        AND DATE(CallDate) BETWEEN :start_date AND :end_date
        GROUP BY DiscountType
        ORDER BY "Total Calls" DESC
    """)

    result = db.execute(query, {"client_id": client_id, "start_date": start_date, "end_date": end_date}).fetchall()
    response_data = [dict(row._mapping) for row in result]

    if response_data:
        total_calls = sum(row["Total Calls"] for row in response_data)
        ops_count = sum(row["OPS Count"] for row in response_data)
        or_count = sum(row["OR Count"] for row in response_data)
        sale_count = sum(row["Sale Count"] for row in response_data)

        grand_total = {
            "Discount Type": "Grand Total",
            "Total Calls": int(total_calls),
            "OPS Count": int(ops_count),
            "OPS%": round(float(ops_count) * 100.0 / max(float(total_calls), 1.0), 2),
            "OR Count": int(or_count),
            "OR%": round(float(or_count) * 100.0 / max(float(total_calls), 1.0), 2),
            "Sale Count": int(sale_count),
            "Conversion%": round(float(sale_count) * 100.0 / max(float(total_calls), 1.0), 2)
        }

        response_data.append(grand_total)

    return response_data


class TranscriptUpdateRequest(BaseModel):
    audio_id: int
    transcript: str


@app.put("/api/update_transcript/")
def update_transcript(request: TranscriptUpdateRequest, db: Session = Depends(get_db)):
    audio = db.query(AudioFile).filter(AudioFile.id == request.audio_id).first()

    if not audio:
        raise HTTPException(status_code=404, detail="Audio file not found")

    audio.transcript = request.transcript
    db.commit()

    return {"status": "success", "message": "Transcript updated"}



###################   Click To Call API Krishna ##########################

@app.get("/api/click2dial")
async def click2dial(
    param1: str = Query(...),
    param2: str = Query(...),
    param3: str = Query(...),
    db: Session = Depends(get_db)  # Inject the database session
):
    target_url = "http://192.168.10.8/remote/click2dial_demo.php"
    params = {
        "customer_number": param1,
        "agent_number": param2,
        "campaignid": param3
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(target_url, params=params)

        try:
            data = response.json()
            # Update user leadid if 'var' is present
            if data.get("var"):
                user = db.query(User).filter(User.contact_number == param2).first()
                if user:
                    user.leadid = data["var"]
                    db.commit()

            return JSONResponse(content={"status": "success", "data": data})
        except Exception:
            return JSONResponse(content={"status": "success", "response": response.text})

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


RECORDING_MAP = {
    "1748262270.2010580": "PLUSH_OB_20250306-160417_7905990690_IDC58359-all.mp3"
}


@app.get("/api/transcribe/{uniqueid}")
async def transcribe(uniqueid: str):
    file_path = RECORDING_MAP.get(uniqueid)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Recording not found.")

    transcript = await transcribe_with_deepgram_async(file_path)
    return {"transcript": transcript}


@app.get("/api/bulk_transcribe")
async def bulk_transcribe(db: Session = Depends(get_db2)):
    result = db.execute(text("SELECT id, recording_path FROM tbl_collection WHERE status = 0"))
    rows = result.fetchall()

    for row in rows:
        id = row[0]
        url = row[1]

        try:
            # Generate a unique temporary filename
            file_name = f"./temp/{uuid.uuid4()}.wav"

            # Ensure temp directory exists
            os.makedirs(os.path.dirname(file_name), exist_ok=True)

            # Download the file using async httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("GET", url) as r:
                    r.raise_for_status()
                    with open(file_name, "wb") as out_file:
                        async for chunk in r.aiter_bytes():
                            out_file.write(chunk)

            # Transcribe
            transcript = await transcribe_with_deepgram_async(file_name)

            # Update DB
            db.execute(
                text("UPDATE tbl_collection SET transcribe_text = :text, status = 1 WHERE id = :id"),
                {"text": transcript, "id": id}
            )
            db.commit()

            print(f"[Success] ID {id} transcribed.")
            os.remove(file_name)

        except Exception as e:
            print(f"[Error] ID {id}: {e}")

    return {"message": "Bulk transcription complete."}


@app.get("/api/analyze/{uniqueid}")
async def analyze(uniqueid: str):
    file_path = RECORDING_MAP.get(uniqueid)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Recording not found.")

    transcript = await transcribe_with_deepgram_async(file_path)
    analysis = await analyze_transcript(transcript)
    return {
        "transcript": transcript,
        "analysis": analysis
    }


@app.get("/api/run_scheduler")
async def run_scheduler(db: Session = Depends(get_db2)):
    query = """
        SELECT c.id, c.recording_path, p.template_text
        FROM tbl_collection c
        JOIN tbl_prompt_demo p ON c.campaign_id = p.ClientId
        WHERE c.status = 0
        LIMIT 5
    """
    results = db.execute(text(query)).fetchall()

    for row in results:
        collection_id, recording_url, prompt_template = row
        print(f"[INFO] Processing collection ID {collection_id}")

        try:
            local_file = f"./temp/{uuid.uuid4()}.wav"
            os.makedirs(os.path.dirname(local_file), exist_ok=True)

            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("GET", recording_url) as r:
                    r.raise_for_status()
                    with open(local_file, "wb") as f:
                        async for chunk in r.aiter_bytes():
                            f.write(chunk)

            transcript = await transcribe_with_deepgram_async(local_file)

            if not transcript or "Transcription failed" in transcript:
                print(f"[ERROR] Transcription failed for ID {collection_id}")
                continue

            final_prompt = (
                prompt_template.replace("{transcribed_text}", transcript)
                if "{transcribed_text}" in prompt_template
                else f"{prompt_template}\n\n{transcript}"
            )
            #print(final_prompt)
            analysis = await analyze_transcript(final_prompt)
            #print(analysis,"ANAlysys 44444444444444444444444444444444444")
            try:
                analysis_json = json.loads(analysis)
            except json.JSONDecodeError:
                analysis_json = {"raw_analysis": analysis}

            # Extract fields
            metadata = analysis_json.get("metadata", {})
            #print(metadata.get("agent_name"),"=======123")
            #break
            ptp_summary = analysis_json.get("ptp_summary", {})
            language_insights = analysis_json.get("language_insights", {})
            followup_priority = analysis_json.get("followup_priority", {})
            ptp_analysis = analysis_json.get("ptp_analysis", {})
            intent_classification = analysis_json.get("intent_classification", {})
            root_cause = analysis_json.get("root_cause", [])
            agent_forced = analysis_json.get("agent_forced_ptp_detected", False)
            escalation_risks = analysis_json.get("escalation_risks", [])
            dispute_mgmt = analysis_json.get("dispute_management", {})
            agent_behavior = analysis_json.get("agent_behavior", {})
            emotion = analysis_json.get("emotional_sentiment", {})
            funnel = analysis_json.get("collection_funnel", {})

            update_query = """
            UPDATE tbl_collection SET
                transcribe_text = :transcribe_text,
                analysis_json = :analysis_json,
                status = 1,

                agent_name = :agent_name,
                team = :team,
                region = :region,
                campaign = :campaign,
                call_disposition = :call_disposition,
                confidence_score = :confidence_score,
                sentiment = :sentiment,

                customer_name = :customer_name,
                ptp_phrase = :ptp_phrase,
                ptp_confidence_score = :ptp_confidence_score,
                predicted_to_fail = :predicted_to_fail,
                ptp_remarks = :ptp_remarks,

                confident_phrases = :confident_phrases,
                hesitation_markers = :hesitation_markers,
                confidence_distribution = :confidence_distribution,

                follow_up_needed = :follow_up_needed,
                priority_level = :priority_level,
                suggested_action = :suggested_action,

                ptp_analysis = :ptp_analysis,
                intent_classification = :intent_classification,
                root_cause = :root_cause,
                agent_forced_ptp_detected = :agent_forced_ptp_detected,
                escalation_risks = :escalation_risks,
                dispute_management = :dispute_management,
                agent_behavior = :agent_behavior,
                emotional_sentiment = :emotional_sentiment,
                collection_funnel = :collection_funnel,
                ptp_amount = :ptp_amount

            WHERE id = :id
            """

            update_params = {
                "id": collection_id,
                "transcribe_text": transcript,
                "analysis_json": json.dumps(analysis_json),

                "agent_name": metadata.get("agent_name"),
                "team": metadata.get("team"),
                "region": metadata.get("region"),
                "campaign": metadata.get("campaign"),
                "call_disposition": metadata.get("call_disposition"),
                "confidence_score": metadata.get("confidence_score"),
                "sentiment": metadata.get("sentiment"),

                "customer_name": ptp_summary.get("customer_name"),
                "ptp_phrase": ptp_summary.get("ptp_phrase"),
                "ptp_confidence_score": ptp_summary.get("confidence_score"),
                "predicted_to_fail": ptp_summary.get("predicted_to_fail"),
                "ptp_remarks": ptp_summary.get("remarks"),
                "ptp_amount": ptp_summary.get("ptp_amount"),
                "confident_phrases": json.dumps(language_insights.get("confident_phrases", [])),
                "hesitation_markers": json.dumps(language_insights.get("hesitation_markers", [])),
                "confidence_distribution": json.dumps(language_insights.get("distribution", {})),

                "follow_up_needed": followup_priority.get("follow_up_needed"),
                "priority_level": followup_priority.get("priority_level"),
                "suggested_action": json.dumps(followup_priority.get("suggested_action", [])),

                "ptp_analysis": json.dumps(ptp_analysis),
                "intent_classification": json.dumps(intent_classification),
                "root_cause": json.dumps(root_cause),
                "agent_forced_ptp_detected": agent_forced,
                "escalation_risks": json.dumps(escalation_risks),
                "dispute_management": json.dumps(dispute_mgmt),
                "agent_behavior": json.dumps(agent_behavior),
                "emotional_sentiment": json.dumps(emotion),
                "collection_funnel": json.dumps(funnel),
            }

            db.execute(text(update_query), update_params)
            db.commit()

            print(f"Updating ID {collection_id} with parameters:\n", update_params)


            print(f"[SUCCESS] Processed ID {collection_id}")

        except Exception as e:
            print(f"[EXCEPTION] Failed ID {collection_id}: {e}")

        finally:
            if os.path.exists(local_file):
                os.remove(local_file)

    return {"message": "Scheduler completed"}



class TranscriptInput(BaseModel):
    transcript: str
    collection_id: int
    prompt_template: str

@app.post("/api/analyze_transcript")
async def analyze_transcript_and_store(data: TranscriptInput, db: Session = Depends(get_db2)):
    try:
        transcript = data.transcript
        collection_id = data.collection_id
        prompt_template = data.prompt_template

        final_prompt = (
            prompt_template.replace("{transcribed_text}", transcript)
            if "{transcribed_text}" in prompt_template
            else f"{prompt_template}\n\n{transcript}"
        )

        analysis = await analyze_transcript(final_prompt)
        try:
            analysis_json = json.loads(analysis)
        except json.JSONDecodeError:
            analysis_json = {"raw_analysis": analysis}

        # Extract fields
        metadata = analysis_json.get("metadata", {})
        ptp_summary = analysis_json.get("ptp_summary", {})
        language_insights = analysis_json.get("language_insights", {})
        followup_priority = analysis_json.get("followup_priority", {})
        ptp_analysis = analysis_json.get("ptp_analysis", {})
        intent_classification = analysis_json.get("intent_classification", {})
        root_cause = analysis_json.get("root_cause", [])
        agent_forced = analysis_json.get("agent_forced_ptp_detected", False)
        escalation_risks = analysis_json.get("escalation_risks", [])
        dispute_mgmt = analysis_json.get("dispute_management", {})
        agent_behavior = analysis_json.get("agent_behavior", {})
        emotion = analysis_json.get("emotional_sentiment", {})
        funnel = analysis_json.get("collection_funnel", {})

        update_query = """
        UPDATE tbl_collection SET
            transcribe_text = :transcribe_text,
            analysis_json = :analysis_json,
            status = 1,

            agent_name = :agent_name,
            team = :team,
            region = :region,
            campaign = :campaign,
            call_disposition = :call_disposition,
            confidence_score = :confidence_score,
            sentiment = :sentiment,

            customer_name = :customer_name,
            ptp_phrase = :ptp_phrase,
            ptp_confidence_score = :ptp_confidence_score,
            predicted_to_fail = :predicted_to_fail,
            ptp_remarks = :ptp_remarks,

            confident_phrases = :confident_phrases,
            hesitation_markers = :hesitation_markers,
            confidence_distribution = :confidence_distribution,

            follow_up_needed = :follow_up_needed,
            priority_level = :priority_level,
            suggested_action = :suggested_action,

            ptp_analysis = :ptp_analysis,
            intent_classification = :intent_classification,
            root_cause = :root_cause,
            agent_forced_ptp_detected = :agent_forced_ptp_detected,
            escalation_risks = :escalation_risks,
            dispute_management = :dispute_management,
            agent_behavior = :agent_behavior,
            emotional_sentiment = :emotional_sentiment,
            collection_funnel = :collection_funnel,
            ptp_amount = :ptp_amount

        WHERE id = :id
        """

        update_params = {
            "id": collection_id,
            "transcribe_text": transcript,
            "analysis_json": json.dumps(analysis_json),

            "agent_name": metadata.get("agent_name"),
            "team": metadata.get("team"),
            "region": metadata.get("region"),
            "campaign": metadata.get("campaign"),
            "call_disposition": metadata.get("call_disposition"),
            "confidence_score": metadata.get("confidence_score"),
            "sentiment": metadata.get("sentiment"),

            "customer_name": ptp_summary.get("customer_name"),
            "ptp_phrase": ptp_summary.get("ptp_phrase"),
            "ptp_confidence_score": ptp_summary.get("confidence_score"),
            "predicted_to_fail": ptp_summary.get("predicted_to_fail"),
            "ptp_remarks": ptp_summary.get("remarks"),
            "ptp_amount": ptp_summary.get("ptp_amount"),
            "confident_phrases": json.dumps(language_insights.get("confident_phrases", [])),
            "hesitation_markers": json.dumps(language_insights.get("hesitation_markers", [])),
            "confidence_distribution": json.dumps(language_insights.get("distribution", {})),

            "follow_up_needed": followup_priority.get("follow_up_needed"),
            "priority_level": followup_priority.get("priority_level"),
            "suggested_action": json.dumps(followup_priority.get("suggested_action", [])),

            "ptp_analysis": json.dumps(ptp_analysis),
            "intent_classification": json.dumps(intent_classification),
            "root_cause": json.dumps(root_cause),
            "agent_forced_ptp_detected": agent_forced,
            "escalation_risks": json.dumps(escalation_risks),
            "dispute_management": json.dumps(dispute_mgmt),
            "agent_behavior": json.dumps(agent_behavior),
            "emotional_sentiment": json.dumps(emotion),
            "collection_funnel": json.dumps(funnel),
        }

        db.execute(text(update_query), update_params)
        db.commit()

        return {"message": f"Collection ID {collection_id} updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/get-leadid")
def get_leadid_by_contact_number(
    contact_number: str = Query(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.contact_number == contact_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "leadid": user.leadid}
