from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routers import clients, jobs, quotes, auth
import uvicorn

app = FastAPI(title="TradeForge")

templates = Jinja2Templates(directory="templates")

# Mount routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(clients.router, prefix="/clients", tags=["clients"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(quotes.router, prefix="/quotes", tags=["quotes"])

@app.get("/")
def home():
    return {"message": "TradeForge API is running! Go to /docs for Swagger UI"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)