"""
Esquemas de validación para las peticiones HTTP
"""
from pydantic import BaseModel
from typing import Dict, List

class GramaticaInput(BaseModel):
    no_terminales: List[str]
    terminales: List[str]
    producciones: Dict[str, List[str]]
    simbolo_inicial: str
    tipo: str

class EvaluarCadenaInput(BaseModel):
    cadena: str

class GenerarCadenasInput(BaseModel):
    n: int = 10
