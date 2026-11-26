from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

RolUsuario = Literal["ADMINISTRADOR", "VENDEDOR", "ENCARGADO_INVENTARIO"]


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str = Field(..., min_length=4, max_length=100)


class UsuarioCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(..., min_length=2, max_length=120)
    correo: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    rol: RolUsuario = "VENDEDOR"


class UsuarioUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    rol: RolUsuario | None = None
    activo: bool | None = None


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    nombre: str
    correo: str
    rol: str
    activo: bool
    creado_en: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut
