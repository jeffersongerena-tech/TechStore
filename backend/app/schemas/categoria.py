from pydantic import BaseModel, ConfigDict, Field


class CategoriaCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(..., min_length=2, max_length=80, description="Nombre único de la categoría")
    descripcion: str | None = Field(default=None, max_length=255)


class CategoriaUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str | None = Field(default=None, min_length=2, max_length=80)
    descripcion: str | None = Field(default=None, max_length=255)
    activa: bool | None = None


class CategoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_categoria: int
    nombre: str
    descripcion: str | None
    activa: bool
