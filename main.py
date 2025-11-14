"""
Punto de entrada de la aplicación
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from api.routes import router
import os

app = FastAPI(title="Analizador Sintactico - Parser de Gramaticas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def root():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)