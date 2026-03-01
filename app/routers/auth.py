from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Usuario
from app.auth import verify_password, crear_sesion, eliminar_sesion, obtener_usuario_sesion

templates = Jinja2Templates(directory="app/templates")
router    = APIRouter(tags=["Auth"])


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    # Si ya tiene sesión, ir directo al dashboard
    if obtener_usuario_sesion(request):
        return RedirectResponse("/views/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login_submit(
    request:  Request,
    email:    str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario or not verify_password(password, usuario.password_hash):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error":   "Email o contraseña incorrectos.",
            "email":   email,   # conservar el email para no tener que reescribirlo
        }, status_code=401)

    response = RedirectResponse("/views/dashboard", status_code=303)
    crear_sesion(response, usuario.id, usuario.email)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=302)
    eliminar_sesion(response)
    return response