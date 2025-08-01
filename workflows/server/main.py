# server/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from workflows.server.routes import campaign_trigger

app = FastAPI()

# Optional: allow calls from your frontend (e.g., Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(campaign_trigger.router)
