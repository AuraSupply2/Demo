"""
auth.py — Sistema de autenticación simple para demo.
Usa cookies firmadas con itsdangerous (sin JWT, sin sesiones complejas).
"""
from fastapi import Request, Form
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from passlib.context import CryptContext
from functools import wraps

from app.config import settings

# ── Crypto ────────────────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer  = URLSafeTimedSerializer(settings.secret_key)

COOKIE_NAME = "session"
COOKIE_MAX_AGE = 60 * 60 * 8  # 8 horas


# ── Password ──────────────────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── Cookie session ────────────────────────────────────────────────────────────
def crear_sesion(response: RedirectResponse, user_id: int, email: str) -> None:
    """Firma los datos del usuario y los guarda en una cookie."""
    token = serializer.dumps({"id": user_id, "email": email})
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,   # no accesible desde JS
        samesite="lax",
    )


def obtener_usuario_sesion(request: Request) -> dict | None:
    """Lee y verifica la cookie. Devuelve el payload o None si inválida/expirada."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        return serializer.loads(token, max_age=COOKIE_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def eliminar_sesion(response: RedirectResponse) -> None:
    response.delete_cookie(COOKIE_NAME)


# ── Guard: redirige al login si no hay sesión ─────────────────────────────────
def login_requerido(request: Request) -> RedirectResponse | None:
    """
    Usar al inicio de cada endpoint protegido:
        redirect = login_requerido(request)
        if redirect: return redirect
    """
    if not obtener_usuario_sesion(request):
        return RedirectResponse("/login", status_code=302)
    return None