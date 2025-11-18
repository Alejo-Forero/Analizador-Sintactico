"""
Implementación del analizador sintáctico usando parsing recursivo descendente con backtracking
"""
from typing import Tuple, Optional, List
from models import Gramatica, ArbolDerivacion

class Parser:
    def __init__(self, gramatica: Gramatica):
        self.gramatica = gramatica
        self.max_profundidad = 100  # Límite de profundidad para evitar recursión infinita

    def parsear(self, cadena: str) -> Tuple[bool, Optional[ArbolDerivacion]]:
        """Determina si una cadena pertenece al lenguaje"""
        resultado = self._parsear_simbolo(self.gramatica.S, cadena, 0, 0)

        # Buscar un resultado que consuma toda la cadena
        for arbol, pos_final in resultado:
            if pos_final == len(cadena):
                return True, arbol

        return False, None

    def _parsear_simbolo(self, simbolo: str, cadena: str, pos: int, profundidad: int) -> List[Tuple[ArbolDerivacion, int]]:
        """
        Parsea un símbolo desde la posición dada.
        Retorna una lista de tuplas (árbol, posición_final) con todas las posibles derivaciones.
        """
        # Límite de profundidad para evitar recursión infinita
        if profundidad > self.max_profundidad:
            return []
        
        resultados = []

        # Si el símbolo es epsilon
        if simbolo == 'ε' or simbolo == '':
            return [(ArbolDerivacion('ε'), pos)]

        # Si el símbolo es terminal
        if simbolo in self.gramatica.T:
            tam = len(simbolo)
            if pos + tam <= len(cadena) and cadena[pos:pos+tam] == simbolo:
                return [(ArbolDerivacion(simbolo), pos + tam)]
            return []

        # Si el símbolo no es un no terminal conocido
        if simbolo not in self.gramatica.N or simbolo not in self.gramatica.P:
            return []

        # Probar cada producción del no terminal
        for produccion in self.gramatica.P[simbolo]:
            for arbol, pos_final in self._parsear_produccion(simbolo, produccion, cadena, pos, profundidad + 1):
                resultados.append((arbol, pos_final))

        return resultados

    def _parsear_produccion(self, no_terminal: str, produccion: str, cadena: str, pos: int, profundidad: int) -> List[Tuple[ArbolDerivacion, int]]:
        """
        Intenta aplicar una producción específica.
        Retorna lista de tuplas (árbol, posición_final).
        """
        nodo = ArbolDerivacion(no_terminal)

        # Manejar producción epsilon
        if produccion == 'ε' or produccion == '':
            nodo.agregar_hijo(ArbolDerivacion('ε'))
            return [(nodo, pos)]

        # Obtener los símbolos de la producción
        simbolos = self._extraer_simbolos(produccion)

        # Parsear los símbolos secuencialmente con backtracking
        resultados = self._parsear_secuencia(simbolos, cadena, pos, profundidad)

        # Construir el árbol para cada resultado válido
        arboles_finales = []
        for hijos, pos_final in resultados:
            nodo_copia = ArbolDerivacion(no_terminal)
            for hijo in hijos:
                nodo_copia.agregar_hijo(hijo)
            arboles_finales.append((nodo_copia, pos_final))

        return arboles_finales

    def _parsear_secuencia(self, simbolos: List[str], cadena: str, pos: int, profundidad: int) -> List[Tuple[List[ArbolDerivacion], int]]:
        """
        Parsea una secuencia de símbolos con backtracking.
        Retorna lista de tuplas (lista_de_arboles, posición_final).
        """
        if not simbolos:
            return [([], pos)]

        primer_simbolo = simbolos[0]
        resto_simbolos = simbolos[1:]

        resultados = []

        # Parsear el primer símbolo
        for arbol_primero, pos_intermedia in self._parsear_simbolo(primer_simbolo, cadena, pos, profundidad):
            # Parsear el resto de la secuencia
            for arboles_resto, pos_final in self._parsear_secuencia(resto_simbolos, cadena, pos_intermedia, profundidad):
                # Combinar resultados
                resultados.append(([arbol_primero] + arboles_resto, pos_final))

        return resultados

    def _extraer_simbolos(self, produccion: str) -> List[str]:
        """
        Extrae los símbolos de una producción (terminales y no terminales).
        Maneja símbolos multi-carácter correctamente e ignora espacios en blanco.
        """
        simbolos = []
        i = 0

        while i < len(produccion):
            # Saltar espacios en blanco
            if produccion[i].isspace():
                i += 1
                continue
                
            simbolo_encontrado = None

            # Buscar no terminales (más largos primero)
            for nt in sorted(self.gramatica.N, key=len, reverse=True):
                if produccion[i:].startswith(nt):
                    simbolo_encontrado = nt
                    break

            # Si no es no terminal, buscar terminal (más largos primero)
            if simbolo_encontrado is None:
                for t in sorted(self.gramatica.T, key=len, reverse=True):
                    if produccion[i:].startswith(t):
                        simbolo_encontrado = t
                        break

            # Si no encontramos nada, tomar un carácter
            if simbolo_encontrado is None:
                simbolo_encontrado = produccion[i]

            simbolos.append(simbolo_encontrado)
            i += len(simbolo_encontrado)

        return simbolos