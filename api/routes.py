"""
Definición de rutas y controladores de la API
"""
import json
import tempfile
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from models.gramatica import Gramatica
from core.parser import Parser
from core.generador import GeneradorCadenas
from schemas.requests import GramaticaInput, EvaluarCadenaInput, GenerarCadenasInput

router = APIRouter()

gramatica_actual: Optional[Gramatica] = None

@router.post("/gramatica")
def definir_gramatica(gramatica_input: GramaticaInput):
    global gramatica_actual

    try:
        gramatica_actual = Gramatica(
            set(gramatica_input.no_terminales),
            set(gramatica_input.terminales),
            gramatica_input.producciones,
            gramatica_input.simbolo_inicial,
            gramatica_input.tipo
        )

        return {
            "mensaje": f"Gramatica {gramatica_input.tipo} definida correctamente",
            "gramatica": gramatica_actual.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al definir gramatica: {str(e)}")

@router.get("/gramatica")
def obtener_gramatica():
    if gramatica_actual is None:
        raise HTTPException(status_code=404, detail="No hay gramatica definida")

    return {
        "gramatica": gramatica_actual.to_dict()
    }

@router.post("/cargar")
async def cargar_gramatica(file: UploadFile = File(...)):
    global gramatica_actual

    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="El archivo debe ser .json")

    try:
        contenido = await file.read()
        data = json.loads(contenido.decode('utf-8'))

        gramatica_actual = Gramatica.from_dict(data)

        return {
            "mensaje": f"Gramatica {gramatica_actual.tipo} cargada correctamente",
            "gramatica": gramatica_actual.to_dict()
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Archivo JSON invalido")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al cargar gramatica: {str(e)}")

@router.get("/descargar")
def descargar_gramatica():
    if gramatica_actual is None:
        raise HTTPException(status_code=404, detail="No hay gramatica definida")

    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8')
    json.dump(gramatica_actual.to_dict(), temp_file, indent=2, ensure_ascii=False)
    temp_file.close()

    return FileResponse(
        temp_file.name,
        media_type='application/json',
        filename='gramatica.json'
    )

@router.post("/evaluar")
def evaluar_cadena(input_data: EvaluarCadenaInput):
    if gramatica_actual is None:
        raise HTTPException(status_code=404, detail="No hay gramatica definida")

    cadena = input_data.cadena
    if cadena == 'ε':
        cadena = ''

    try:
        parser = Parser(gramatica_actual)
        aceptada, arbol = parser.parsear(cadena)

        if aceptada:
            return {
                "aceptada": True,
                "mensaje": "CADENA ACEPTADA",
                "cadena": input_data.cadena if input_data.cadena else 'ε',
                "arbol_derivacion": arbol.to_dict(),
                "arbol_texto": arbol.to_text()
            }
        else:
            return {
                "aceptada": False,
                "mensaje": "CADENA RECHAZADA",
                "cadena": input_data.cadena if input_data.cadena else 'ε'
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al evaluar cadena: {str(e)}")

@router.post("/generar")
def generar_cadenas(input_data: GenerarCadenasInput):
    if gramatica_actual is None:
        raise HTTPException(status_code=404, detail="No hay gramatica definida")

    try:
        generador = GeneradorCadenas(gramatica_actual)
        cadenas = generador.generar_primeras_n(input_data.n)

        cadenas_display = [c if c else 'ε' for c in cadenas]

        return {
            "total_generadas": len(cadenas),
            "cadenas": cadenas_display
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar cadenas: {str(e)}")

@router.delete("/gramatica")
def eliminar_gramatica():
    global gramatica_actual

    if gramatica_actual is None:
        raise HTTPException(status_code=404, detail="No hay gramatica definida")

    gramatica_actual = None
    return {"mensaje": "Gramatica eliminada correctamente"}
