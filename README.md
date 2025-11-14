## Descripción

Este proyecto implementa un analizador sintáctico completo que permite:
- Definir gramáticas formales (Tipo 2 y Tipo 3)
- Evaluar si una cadena pertenece al lenguaje generado por la gramática
- Visualizar el árbol de derivación de cadenas aceptadas
- Generar las primeras 10 cadenas más cortas del lenguaje
- Guardar y cargar gramáticas en formato JSON

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Estructura del Proyecto

```
proyecto/
├── main.py                    # Punto de entrada de la aplicación
├── models/                    # Modelos de dominio
│   ├── __init__.py
│   ├── gramatica.py          # Clase Gramatica
│   └── arbolDerivacion.py    # Clase ArbolDerivacion
├── core/                      # Lógica de negocio
│   ├── __init__.py
│   ├── parser.py             # Analizador sintáctico
│   └── generador.py          # Generador de cadenas
├── schemas/                   # Validación de datos
│   ├── __init__.py
│   └── requests.py           # Esquemas Pydantic
├── api/                       # Capa de presentación
│   ├── __init__.py
│   └── routes.py             # Endpoints REST
├── templates/                 # Frontend
│   └── index.html            # Interfaz de usuario
```
## Instalación

### 1. Clonar o descargar el proyecto

- bash
- git clone 
- cd proyecto

### 2. Instalar dependencias

pip install fastapi uvicorn python-multipart

## Ejecución

python main.py

### Acceder a la aplicación

Abre tu navegador web en: http://localhost:8000
