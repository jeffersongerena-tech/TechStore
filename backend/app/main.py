from fastapi import FastAPI

app = FastAPI(title="TechStore API", version="0.1.0")

@app.get("/")
def root():
    return {"mensaje": "API de TechStore funcionando correctamente"}