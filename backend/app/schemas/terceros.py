from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProveedorCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(..., min_length=2, max_length=120)
    documento: str = Field(..., min_length=3, max_length=30, description="NIT o documento único del proveedor")
    telefono: str | None = Field(default=None, max_length=30)
    correo: EmailStr | None = None
    direccion: str | None = Field(default=None, max_length=200)


class ProveedorUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    documento: str | None = Field(default=None, min_length=3, max_length=30)
    telefono: str | None = Field(default=None, max_length=30)
    correo: EmailStr | None = None
    direccion: str | None = Field(default=None, max_length=200)
    activo: bool | None = None


class ProveedorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_proveedor: int
    nombre: str
    documento: str
    telefono: str | None
    correo: str | None
    direccion: str | None
    activo: bool


class ClienteCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(..., min_length=2, max_length=120)
    documento: str = Field(..., min_length=3, max_length=30, description="Documento único del cliente")
    telefono: str | None = Field(default=None, max_length=30)
    correo: EmailStr | None = None


class ClienteUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    documento: str | None = Field(default=None, min_length=3, max_length=30)
    telefono: str | None = Field(default=None, max_length=30)
    correo: EmailStr | None = None
    activo: bool | None = None


class ClienteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cliente: int
    nombre: str
    documento: str
    telefono: str | None
    correo: str | None
    activo: bool
