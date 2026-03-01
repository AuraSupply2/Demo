from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Pedido, Cliente, EstadoPedido
from app.schemas.schemas import DashboardOut, PedidoResumen

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardOut)
def obtener_dashboard(db: Session = Depends(get_db)):

    # ── 1. Conteos y suma en una sola pasada por la tabla ──────────────────
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
        )
        .one()
    )

    # ── 2. Últimos 5 pedidos con nombre de cliente (join, sin N+1) ─────────
    ultimos = (
        db.query(Pedido, Cliente.nombre.label("cliente_nombre"))
        .join(Cliente, Pedido.cliente_id == Cliente.id)
        .order_by(Pedido.creado_en.desc())
        .limit(5)
        .all()
    )

    ultimos_pedidos = [
        PedidoResumen(
            id=pedido.id,
            descripcion=pedido.descripcion,
            precio=pedido.precio,
            status=pedido.status,
            creado_en=pedido.creado_en,
            cliente_nombre=cliente_nombre,
        )
        for pedido, cliente_nombre in ultimos
    ]

    return DashboardOut(
        pedidos_activos=stats.activos,
        pedidos_pendientes=stats.pendientes,
        total_facturado=round(stats.facturado, 2),
        ultimos_pedidos=ultimos_pedidos,
    )