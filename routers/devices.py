from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db
from routers.auth import get_current_user
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        user = get_current_user(request)
    except:
        return RedirectResponse(url="/auth/login-page")
    conn = get_db()
    devices = conn.execute("SELECT * FROM devices").fetchall()
    conn.close()
    return templates.TemplateResponse("dashboard.html", {"request": request, "devices": devices, "user": user})

@router.post("/toggle/{device_id}")
async def toggle_device(device_id: int, request: Request):
    try:
        user = get_current_user(request)
    except:
        return RedirectResponse(url="/auth/login-page")
    conn = get_db()
    cursor = conn.cursor()
    device = cursor.execute("SELECT * FROM devices WHERE id=?", (device_id,)).fetchone()
    if not device:
        conn.close()
        return {"error": "Устройство не найдено"}
    new_status = "on" if device["status"] == "off" else "off"
    cursor.execute("UPDATE devices SET status=? WHERE id=?", (new_status, device_id))
    # запись в лог
    cursor.execute("INSERT INTO event_log (device_id, event_type, description) VALUES (?, 'toggle', ?)",
        (device_id, f"Устройство '{device['name']}' переключено в {new_status}"))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/dashboard", status_code=302)