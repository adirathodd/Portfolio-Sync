import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from resume_parser import ResumeParser
from pydantic import BaseModel, EmailStr
from typing import Optional
from supa import UserManager
from datetime import datetime, timedelta
import jwt
import os
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
engine = ResumeParser()
users = UserManager()

# JWT config
SECRET_KEY = os.getenv("JWT_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
 
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Generate a JWT token with expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
 
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validate JWT bearer token and return the username."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(login_request: LoginRequest):
    """Authenticate a user by username and password."""
    try:
        success, message = users.verify(login_request.username, login_request.password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if success:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": login_request.username},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail=message)

@app.post("/signup")
async def signup(signup_request: SignupRequest):
    try:
        response, message = users.add_user(signup_request.model_dump())

        if response:
            return {"message": message}
        else:
            return {"error": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/scrape")
async def scrape_pdf(
    pdf_file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF.")

    file_contents = await pdf_file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_contents)
        tmp_filepath = tmp.name

    try:
        result = engine.parse(tmp_filepath)
    finally:
        os.remove(tmp_filepath)

    return {"filename": pdf_file.filename, "result": result}