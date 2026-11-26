class TechStoreException(Exception):
    def __init__(self, mensaje: str, status_code: int = 400):
        self.mensaje = mensaje
        self.status_code = status_code
        super().__init__(mensaje)


class RecursoNoEncontradoError(TechStoreException):
    def __init__(self, mensaje: str):
        super().__init__(mensaje, status_code=404)


class ConflictoNegocioError(TechStoreException):
    def __init__(self, mensaje: str):
        super().__init__(mensaje, status_code=409)


class StockInsuficienteError(TechStoreException):
    def __init__(self, mensaje: str):
        super().__init__(mensaje, status_code=400)


class PermisoDenegadoError(TechStoreException):
    def __init__(self, mensaje: str = "No tiene permisos para ejecutar esta operación."):
        super().__init__(mensaje, status_code=403)
