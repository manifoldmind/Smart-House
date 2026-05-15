from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db
import bcrypt
import uuid

router = APIRouter()

# Временное хранилище сессий (в реальном проекте — Redis или БД)
sessions = {}

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Не авторизован")
    return sessions[session_id]  # возвращает dict с user_id и ролью

@router.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    conn = get_db()
    try:
        cursor = conn.cursor()
        # проверка уникальности
        row = cursor.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if row:
            raise HTTPException(status_code=400, detail="Пользователь уже существует")
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'resident')",
            (username, hashed))
        conn.commit()
        # автоматически авторизуем
        user_id = cursor.lastrowid
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"user_id": user_id, "role": "resident"}
        resp = RedirectResponse(url="/dashboard", status_code=302)
        resp.set_cookie("session_id", session_id)
        return resp
    finally:
        conn.close()

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = get_db()
    try:
        cursor = conn.cursor()
        row = cursor.execute("SELECT id, password_hash, role FROM users WHERE username=?", (username,)).fetchone()
        if not row or not bcrypt.checkpw(password.encode('utf-8'), row["password_hash"]):
            raise HTTPException(status_code=400, detail="Неверное имя или пароль")
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"user_id": row["id"], "role": row["role"]}
        resp = RedirectResponse(url="/dashboard", status_code=302)
        resp.set_cookie("session_id", session_id)
        return resp
    finally:
        conn.close()

@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/")
    resp.delete_cookie("session_id")
    return resp

@router.get("/login-page", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})