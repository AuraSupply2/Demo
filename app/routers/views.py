from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.models import Pedido, Cliente, EstadoPedido
from app.auth import login_requerido, obtener_usuario_sesion

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/views", tags=["Views"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _dashboard_data(db: Session) -> dict:
    stats = (
        db.query(
            func.count().filter(
                Pedido.status.in_([EstadoPedido.pending, EstadoPedido.in_progress])
            ).label("activos"),
            func.count().filter(
                Pedido.status == EstadoPedido.pending
            ).label("pendientes"),
            func.coalesce(
                func.sum(Pedido.precio).filter(Pedido.status == EstadoPedido.delivered),
                0.0,
            ).label("facturado"),
        ).one()
    )
    ultimos = (
        db.query(Pedido, Cliente.nombre.label("cliente_nombre"))
        .join(Cliente, Pedido.cliente_id == Cliente.id)
        .order_by(Pedido.creado_en.desc())
        .limit(5)
        .all()
    )
    return {
        "pedidos_activos":    stats.activos,
        "pedidos_pendientes": stats.pendientes,
        "total_facturado":    round(stats.facturado, 2),
        "ultimos_pedidos": [
            type("PedidoResumen", (), {
                "id":             p.id,
                "descripcion":    p.descripcion,
                "precio":         p.precio,
                "status":         p.status,
                "creado_en":      p.creado_en,
                "cliente_nombre": cn,
            })() for p, cn in ultimos
        ],
    }


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_class=HTMLResponse)
def vista_dashboard(request: Request, db: Session = Depends(get_db)):
    if (r := login_requerido(request)): return r

    total_clientes = db.query(func.count(Cliente.id)).scalar()
    data = _dashboard_data(db)
    usuario = obtener_usuario_sesion(request)
    return templates.TemplateResponse("views/dashboard.html", {
        "request":        request,
        "active":         "dashboard",
        "data":           type("D", (), data)(),
        "total_clientes": total_clientes,
        "usuario":        usuario,
    })


# ── Clientes ──────────────────────────────────────────────────────────────────

@router.get("/clientes", response_class=HTMLResponse)
def vista_clientes(request: Request, db: Session = Depends(get_db),
                   msg: Optional[str] = None, msg_type: Optional[str] = None):
    if (r := login_requerido(request)): return r

    clientes = db.query(Cliente).order_by(Cliente.id.desc()).all()
    return templates.TemplateResponse("views/clientes.html", {
        "request":  request,
        "active":   "clientes",
        "clientes": clientes,
        "msg":      msg,
        "msg_type": msg_type or "success",
        "usuario":  obtener_usuario_sesion(request),
    })


@router.post("/clientes")
def crear_cliente_vista(
    request:  Request,
    nombre:   str = Form(...),
    email:    str = Form(...),
    telefono: str = Form(""),
    db: Session = Depends(get_db),
):
    if (r := login_requerido(request)): return r

    existente = db.query(Cliente).filter(Cliente.email == email).first()
    if existente:
        return RedirectResponse(
            "/views/clientes?msg=Ya+existe+un+cliente+con+ese+email&msg_type=danger",
            status_code=303,
        )
    cliente = Cliente(nombre=nombre, email=email, telefono=telefono or None)
    db.add(cliente)
    db.commit()
    return RedirectResponse(
        f"/views/clientes?msg=Cliente+{nombre}+creado+exitosamente&msg_type=success",
        status_code=303,
    )


@router.post("/clientes/{cliente_id}/eliminar")
def eliminar_cliente_vista(
    request: Request,
    cliente_id: int,
    db: Session = Depends(get_db),
):
    if (r := login_requerido(request)): return r

    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente:
        db.delete(cliente)
        db.commit()
    return RedirectResponse(
        "/views/clientes?msg=Cliente+eliminado&msg_type=success",
        status_code=303,
    )


# ── Pedidos ───────────────────────────────────────────────────────────────────

@router.get("/pedidos", response_class=HTMLResponse)
def vista_pedidos(
    request:  Request,
    db:       Session = Depends(get_db),
    status:   Optional[str] = None,
    msg:      Optional[str] = None,
    msg_type: Optional[str] = None,
):
    if (r := login_requerido(request)): return r

    query = db.query(Pedido)
    if status:
        try:
            query = query.filter(Pedido.status == EstadoPedido(status))
        except ValueError:
            pass

    pedidos  = query.order_by(Pedido.id.desc()).all()
    clientes = db.query(Cliente).filter(Cliente.activo == True).all()

    return templates.TemplateResponse("views/pedidos.html", {
        "request":       request,
        "active":        "pedidos",
        "pedidos":       pedidos,
        "clientes":      clientes,
        "status_filter": status or "",
        "msg":           msg,
        "msg_type":      msg_type or "success",
        "usuario":       obtener_usuario_sesion(request),
    })


@router.post("/pedidos")
def crear_pedido_vista(
    request:     Request,
    cliente_id:  int   = Form(...),
    descripcion: str   = Form(...),
    precio:      float = Form(...),
    db: Session = Depends(get_db),
):
    if (r := login_requerido(request)): return r

    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        return RedirectResponse(
            "/views/pedidos?msg=Cliente+no+encontrado&msg_type=danger",
            status_code=303,
        )
    pedido = Pedido(cliente_id=cliente_id, descripcion=descripcion, precio=precio)
    db.add(pedido)
    db.commit()
    return RedirectResponse(
        "/views/pedidos?msg=Pedido+creado+exitosamente&msg_type=success",
        status_code=303,
    )


@router.post("/pedidos/{pedido_id}/status")
def cambiar_estado_vista(
    request:   Request,
    pedido_id: int,
    status:    str = Form(...),
    db: Session = Depends(get_db),
):
    if (r := login_requerido(request)): return r

    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido:
        try:
            pedido.status = EstadoPedido(status)
            db.commit()
        except ValueError:
            pass
    return RedirectResponse(
        "/views/pedidos?msg=Estado+actualizado&msg_type=success",
        status_code=303,
    )


@router.post("/pedidos/{pedido_id}/eliminar")
def eliminar_pedido_vista(
    request:   Request,
    pedido_id: int,
    db: Session = Depends(get_db),
):
    if (r := login_requerido(request)): return r

    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido:
        db.delete(pedido)
        db.commit()
    return RedirectResponse(
        "/views/pedidos?msg=Pedido+eliminado&msg_type=success",
        status_code=303,
    )