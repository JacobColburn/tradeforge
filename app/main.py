from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

app = FastAPI(title="TradeForge")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Fake in-memory users (admin + demo)
users_db = {
    "admin@tradeforge.com": {
        "username": "admin",
        "email": "admin@tradeforge.com",
        "hashed_password": "$2b$12$placeholderhash",  # we'll handle hashing properly
        "role": "admin"
    },
    "tech@tradeforge.com": {
        "username": "tech",
        "email": "tech@tradeforge.com",
        "hashed_password": "$2b$12$placeholderhash",
        "role": "tech"
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "supersecretkeychangemeinproduction"
ALGORITHM = "HS256"

class User(BaseModel):
    email: str
    username: str
    role: str

# Fake data
leads = [
    {"id": 1, "customer": "John Smith", "phone": "(214) 555-0123", "message": "AC not cooling - Lewisville", "time": "2 hours ago", "status": "New"},
    {"id": 2, "customer": "Maria Garcia", "phone": "(972) 555-0456", "message": "Leaking pipe under sink", "time": "Yesterday", "status": "Callback"}
]

ongoing_jobs = [
    {"id": 101, "customer": "Bob Johnson", "job": "HVAC Install", "status": "In Progress", "due": "Today", "tech": "You"},
    {"id": 102, "customer": "Sarah Lee", "job": "Electrical Panel Upgrade", "status": "Scheduled", "due": "Tomorrow", "tech": "You"}
]

kb_articles = [
    {"title": "Common AC Issues in Texas Heat", "summary": "Quick troubleshooting for high temps."},
    {"title": "How to Handle Emergency Calls", "summary": "Best practices for voicemails and callbacks."}
]

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Optional[str] = None):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email not in users_db:
            return None
        user_dict = users_db[email]
        return User(email=email, username=user_dict["username"], role=user_dict["role"])
    except:
        return None

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    user = users_db.get(email)
    if user and password == "password123":  # simple demo password
        token = create_access_token({"sub": email})
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response
    return RedirectResponse(url="/login?error=Invalid credentials", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    token = request.cookies.get("access_token")
    user = get_current_user(token)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "leads": leads,
        "ongoing_jobs": ongoing_jobs,
        "kb_articles": kb_articles
    })

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
