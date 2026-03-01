from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal

# Importar todos los modelos antes de create_all
from app.models import models  # noqa: F401
from app.models.models import Usuario
from app.auth import hash_password

from app.routers import productos, clientes, pedidos, dashboard, views, auth


def _seed_usuario_demo(db: Session) -> None:
    """Crea el usuario admin de demo si no existe."""
    existe = db.query(Usuario).filter(Usuario.email == "admin@demo.com").first()
    if not existe:
        admin = Usuario(
            nombre        = "Admin Demo",
            email         = "admin@demo.com",
            password_hash = hash_password("admin123"),
        )
        db.add(admin)
        db.commit()
        print("👤 Usuario demo creado: admin@demo.com / admin123")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas/verificadas en la base de datos.")
    db = SessionLocal()
    try:
        _seed_usuario_demo(db)
    finally:
        db.close()
    yield
    print("👋 Aplicación cerrada.")


app = FastAPI(
    title=settings.app_name,
    description="Sistema de gestión para pequeños negocios - DEMO",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)
origins = [
    "http://localhost:5173",
    "https://demo-qze7.onrender.com",  # opcional
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Auth (login / logout) — sin prefijo para tener /login y /logout limpios
app.include_router(auth.router)

# API routers
app.include_router(productos.router, prefix="/api/v1")
app.include_router(clientes.router,  prefix="/api/v1")
app.include_router(pedidos.router,   prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")

# View routers (Jinja2 templates)
app.include_router(views.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/views/dashboard")


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}