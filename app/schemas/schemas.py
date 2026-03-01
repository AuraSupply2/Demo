from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.models import EstadoPedido


# --- Producto ---
class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int = 0
    activo: bool = True


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    activo: Optional[bool] = None


class ProductoOut(ProductoBase):
    id: int
    creado_en: datetime

    model_config = {"from_attributes": True}


# --- Cliente ---
class ClienteBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    activo: bool = True


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class ClienteOut(ClienteBase):
    id: int
    creado_en: datetime

    model_config = {"from_attributes": True}


# --- Pedido ---
class PedidoCreate(BaseModel):
    cliente_id: int
    descripcion: str
    precio: float


class PedidoEstadoUpdate(BaseModel):
    status: EstadoPedido


class ClienteResumen(BaseModel):
    id: int
    nombre: str
    email: str

    model_config = {"from_attributes": True}


class PedidoOut(BaseModel):
    id: int
    cliente_id: int
    descripcion: str
    precio: float
    status: EstadoPedido
    creado_en: datetime
    cliente: ClienteResumen

    model_config = {"from_attributes": True}


# --- Dashboard ---
class PedidoResumen(BaseModel):
    id: int
    descripcion: str
    precio: float
    status: EstadoPedido
    creado_en: datetime
    cliente_nombre: str

    model_config = {"from_attributes": True}


class DashboardOut(BaseModel):
    pedidos_activos: int        # pending + in_progress
    pedidos_pendientes: int     # solo pending
    total_facturado: float      # suma precio de delivered
    ultimos_pedidos: list[PedidoResumen]