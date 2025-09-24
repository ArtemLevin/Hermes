from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, students, dashboard

app = FastAPI(title="Tutor MVP", version="0.1")

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/health")
def health():
    return {"status": "ok"}

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(students.router, prefix="/students", tags=["students"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
