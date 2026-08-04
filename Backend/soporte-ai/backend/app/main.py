import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.tickets import router

load_dotenv()

app = FastAPI(title="Soporte AI - Tickets SAP")

# CORS (para el frontend React). En producción, definir CORS_ORIGINS
# en .env como una lista separada por comas, p.ej: "https://mi-dashboard.com"
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"status": "running"}
