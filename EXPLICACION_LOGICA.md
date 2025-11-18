# Explicación de la Lógica del Analizador Sintáctico

## Índice
1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Componentes Principales](#componentes-principales)
4. [Flujo de Trabajo](#flujo-de-trabajo)
5. [Algoritmos Implementados](#algoritmos-implementados)

---

## Visión General

Este proyecto implementa un **analizador sintáctico (parser)** completo que puede:
- Trabajar con gramáticas formales de Tipo 2 (libres de contexto) y Tipo 3 (regulares)
- Determinar si una cadena pertenece al lenguaje definido por la gramática
- Construir el árbol de derivación de cadenas aceptadas
- Generar automáticamente cadenas válidas del lenguaje

El sistema utiliza **FastAPI** como framework web para proporcionar una API REST y una interfaz web interactiva.

---

## Arquitectura del Sistema

### Patrón de Capas

El proyecto sigue una arquitectura de capas bien definida:

```
┌─────────────────────────────────────┐
│      Capa de Presentación           │
│  (API REST + Frontend HTML)         │
│  - routes.py                        │
│  - index.html                       │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│      Capa de Validación             │
│  (Esquemas Pydantic)                │
│  - requests.py                      │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│      Capa de Lógica de Negocio      │
│  - Parser (parser.py)               │
│  - Generador (generador.py)         │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│      Capa de Modelos                │
│  - Gramatica                        │
│  - ArbolDerivacion                  │
└─────────────────────────────────────┘
```

---

## Componentes Principales

### 1. **Modelo de Gramática** (`models/gramatica.py`)

Define la estructura de una gramática formal `G = (N, T, P, S)`:

```python
class Gramatica:
    N: Set[str]                    # Conjunto de no terminales
    T: Set[str]                    # Conjunto de terminales
    P: Dict[str, List[str]]        # Producciones (no_terminal -> [producción1, ...])
    S: str                         # Símbolo inicial
    tipo: str                      # Tipo de gramática ("Tipo 2" o "Tipo 3")
```

**Funcionalidad:**
- Almacena la definición formal de la gramática
- Métodos de serialización/deserialización (`to_dict`, `from_dict`)
- Facilita la persistencia en formato JSON

### 2. **Modelo de Árbol de Derivación** (`models/arbolDerivacion.py`)

Representa el árbol de derivación de una cadena:

```python
class ArbolDerivacion:
    simbolo: str                   # Símbolo del nodo (terminal o no terminal)
    hijos: List[ArbolDerivacion]   # Hijos del nodo
```

**Funcionalidad:**
- Estructura de árbol n-ario para representar derivaciones
- Método `to_dict()` para serialización JSON
- Método `to_text()` para representación textual indentada

### 3. **Parser** (`core/parser.py`)

Implementa el **analizador sintáctico con parsing recursivo descendente y backtracking**.

#### Algoritmo Principal

El parser utiliza una estrategia de **análisis descendente predictivo con backtracking**:

```
parsear(cadena):
    1. Intentar derivar desde el símbolo inicial S
    2. Probar todas las producciones posibles
    3. Si una derivación completa consume toda la cadena → ACEPTAR
    4. Si ninguna derivación funciona → RECHAZAR
```

#### Métodos Clave

**`parsear(cadena)`**
- Punto de entrada del parser
- Retorna `(bool, ArbolDerivacion)` indicando si acepta y el árbol de derivación

**`_parsear_simbolo(simbolo, cadena, pos)`**
- Parsea un símbolo individual desde una posición
- Retorna lista de posibles `(árbol, posición_final)`
- Casos:
  - **Epsilon (ε)**: No consume entrada, retorna posición actual
  - **Terminal**: Verifica coincidencia exacta con la cadena
  - **No terminal**: Prueba todas sus producciones

**`_parsear_produccion(no_terminal, produccion, cadena, pos)`**
- Aplica una producción específica
- Descompone la producción en símbolos
- Intenta parsear la secuencia completa

**`_parsear_secuencia(simbolos, cadena, pos)`**
- **Implementa backtracking**
- Parsea símbolos secuencialmente
- Si el primer símbolo falla, prueba alternativas
- Retorna todas las combinaciones válidas

**`_extraer_simbolos(produccion)`**
- Descompone una producción en símbolos individuales
- Maneja símbolos multi-carácter correctamente
- Prioriza símbolos más largos (greedy matching)

#### Ejemplo de Backtracking

Para la gramática:
```
S -> AB | A
A -> a
B -> b
```

Al parsear "a":
1. Prueba `S -> AB`
   - Parsea `A -> a` (consume "a", pos=1)
   - Intenta parsear `B` desde pos=1 (falla, no hay más entrada)
   - **Backtrack**
2. Prueba `S -> A`
   - Parsea `A -> a` (consume "a", pos=1)
   - Éxito, pos=1 == longitud("a")
   - **ACEPTA**

### 4. **Generador de Cadenas** (`core/generador.py`)

Genera las primeras N cadenas más cortas del lenguaje usando **BFS (Búsqueda en Anchura)**.

#### Algoritmo BFS

```python
generar_primeras_n(n):
    1. Iniciar con el símbolo inicial S en la cola
    2. Mientras haya formas sentenciales y no tengamos n cadenas:
       a. Extraer forma sentencial de la cola
       b. Si es terminal → agregar a resultados
       c. Si tiene no terminales → expandir el primero con todas sus producciones
       d. Agregar nuevas formas a la cola
    3. Ordenar por longitud y retornar las primeras n
```

#### Ventajas de BFS

- **Garantiza las cadenas más cortas primero**: BFS explora por niveles
- **Evita derivaciones infinitas**: Limita profundidad y longitud
- **Eficiente**: Usa conjunto de visitados para evitar repeticiones

#### Métodos Clave

**`generar_primeras_n(n)`**
- Usa cola FIFO para BFS
- Controla profundidad máxima (20) y longitud (100)
- Evita estados duplicados con conjunto `visitados`

**`_encontrar_primer_no_terminal(forma)`**
- Encuentra el primer no terminal en la forma sentencial
- Estrategia leftmost (más a la izquierda)
- Maneja símbolos multi-carácter

#### Ejemplo de Generación

Para `S -> ε | aS`:
```
Nivel 0: [S]
Nivel 1: [ε, aS]  → genera "ε"
Nivel 2: [aε, aaS] → genera "a"
Nivel 3: [aaε, aaaS] → genera "aa"
...
Resultado: ["ε", "a", "aa", "aaa", ...]
```

### 5. **API REST** (`api/routes.py`)

Proporciona endpoints RESTful para interactuar con el sistema:

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/gramatica` | POST | Define una nueva gramática |
| `/api/gramatica` | GET | Obtiene la gramática actual |
| `/api/gramatica` | DELETE | Elimina la gramática actual |
| `/api/cargar` | POST | Carga gramática desde archivo JSON |
| `/api/descargar` | GET | Descarga la gramática actual |
| `/api/evaluar` | POST | Evalúa si una cadena es aceptada |
| `/api/generar` | POST | Genera N cadenas del lenguaje |

**Estado Global:**
- Mantiene `gramatica_actual` en memoria
- Accesible desde todos los endpoints

---

## Flujo de Trabajo

### Flujo 1: Evaluar una Cadena

```
Usuario → Frontend → POST /api/evaluar
                           ↓
                     Validar entrada (Pydantic)
                           ↓
                     Parser.parsear(cadena)
                           ↓
                     ┌──── Backtracking ────┐
                     │  Probar producciones │
                     │  Construir árbol     │
                     └──────────────────────┘
                           ↓
                ┌──────────┴──────────┐
                ↓                     ↓
           ACEPTADA              RECHAZADA
        (con árbol)           (sin árbol)
                ↓                     ↓
              JSON                  JSON
                ↓                     ↓
            Frontend              Frontend
```

### Flujo 2: Generar Cadenas

```
Usuario → Frontend → POST /api/generar
                           ↓
                     GeneradorCadenas.generar_primeras_n(n)
                           ↓
                     ┌──── BFS ────┐
                     │ Cola = [S]  │
                     │ Expandir    │
                     │ por niveles │
                     └─────────────┘
                           ↓
                   Ordenar por longitud
                           ↓
                   Retornar primeras N
                           ↓
                         JSON
                           ↓
                       Frontend
```

### Flujo 3: Definir Gramática

```
Usuario ingresa:
- No terminales: [S, A]
- Terminales: [a, b]
- Producciones: {S: [aA, ε], A: [bS]}
- Símbolo inicial: S
                ↓
         POST /api/gramatica
                ↓
         Validación Pydantic
                ↓
         Crear objeto Gramatica
                ↓
         Almacenar globalmente
                ↓
         Respuesta JSON
```

---

## Algoritmos Implementados

### 1. **Parsing Recursivo Descendente con Backtracking**

**Complejidad:** O(k^n) en el peor caso, donde:
- k = número promedio de producciones por no terminal
- n = longitud de la cadena

**Características:**
- **Completo**: Encuentra solución si existe
- **Correcto**: Solo acepta cadenas válidas
- **Ineficiente** para gramáticas ambiguas (múltiples derivaciones)

**Optimizaciones:**
- Memorización de estados visitados
- Poda de derivaciones muy largas

### 2. **BFS para Generación de Cadenas**

**Complejidad:** O(k^d) donde:
- k = factor de ramificación (producciones)
- d = profundidad máxima

**Características:**
- **Optimalidad**: Encuentra cadenas más cortas primero
- **Completitud**: Explora todo el espacio de derivaciones
- **Control**: Límites de profundidad y longitud evitan bucles infinitos

### 3. **Reconocimiento de Símbolos Multi-carácter**

Ambos parser y generador usan **greedy matching**:
- Ordenan símbolos por longitud (descendente)
- Intentan coincidir el símbolo más largo primero
- Evita ambigüedades (e.g., "ab" vs "a" + "b")

---

## Consideraciones Técnicas

### Manejo de Epsilon (ε)

- **Cadena vacía** se representa como `''` internamente
- En la interfaz se muestra como `'ε'`
- Las producciones epsilon no consumen entrada

### Persistencia

- **Formato JSON** para almacenar gramáticas
- Serialización mediante `to_dict()` y `from_dict()`
- Descarga/carga de archivos vía API

### Concurrencia

- **Sin estado compartido mutable** (excepto `gramatica_actual`)
- Cada request crea objetos Parser/Generador nuevos
- Thread-safe para lecturas (FastAPI maneja concurrencia)

### Validación

- **Pydantic** valida esquemas de entrada automáticamente
- Errores HTTP 400 para datos inválidos
- Errores HTTP 500 para fallos internos

---

## Ejemplo Completo

### Gramática de Paréntesis Balanceados

```
N = {S}
T = {(, )}
S = S
P = {
    S -> (S) | SS | ε
}
```

### Proceso de Evaluación para "(())"

1. **Inicio**: `_parsear_simbolo(S, "(())", 0)`

2. **Probar S -> (S)**:
   - Parsear "(" en pos 0 → éxito, pos=1
   - Parsear S en pos 1:
     - Probar S -> (S):
       - Parsear "(" en pos 1 → éxito, pos=2
       - Parsear S en pos 2:
         - Probar S -> ε → éxito, pos=2
       - Parsear ")" en pos 2 → éxito, pos=3
   - Parsear ")" en pos 3 → éxito, pos=4
   - **pos=4 == len("(())") → ACEPTAR**

3. **Árbol generado**:
```
S
├── (
├── S
│   ├── (
│   ├── S
│   │   └── ε
│   └── )
└── )
```

### Generación de Cadenas

**BFS**:
```
Nivel 0: S
Nivel 1: (S), SS, ε          → genera "ε"
Nivel 2: ((S)), (S)S, S(S), ... → genera "()", ...
...
Resultado: ["ε", "()", "()()", "(())", ...]
```

---

## Conclusión

Este analizador sintáctico es un sistema completo que combina:
- **Teoría de lenguajes formales** (gramáticas, derivaciones)
- **Algoritmos de búsqueda** (backtracking, BFS)
- **Ingeniería de software** (arquitectura en capas, API REST)
- **Interfaz web** interactiva y amigable

Es especialmente útil para:
- Educación en teoría de la computación
- Validación de lenguajes formales
- Prototipado de gramáticas
- Comprensión visual de derivaciones
