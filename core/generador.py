"""
Generador de cadenas del lenguaje usando BFS
"""
from collections import deque
from typing import List
from models.gramatica import Gramatica

class GeneradorCadenas:
    def __init__(self, gramatica: Gramatica):
        self.gramatica = gramatica

    def generar_primeras_n(self, n: int = 10) -> List[str]:
        """
        Genera las primeras n cadenas más cortas del lenguaje usando BFS.
        """
        cadenas_generadas = set()
        cola = deque([(self.gramatica.S, 0)])
        visitados = set()
        max_profundidad = 20

        while cola and len(cadenas_generadas) < n:
            forma_sentencial, profundidad = cola.popleft()

            if profundidad > max_profundidad:
                continue

            estado = forma_sentencial
            if estado in visitados:
                continue
            visitados.add(estado)

            # Verificar si es una cadena terminal
            primer_no_terminal = self._encontrar_primer_no_terminal(forma_sentencial)

            if primer_no_terminal is None:
                # Es una cadena terminal
                cadena_final = forma_sentencial.replace('ε', '')
                if cadena_final not in cadenas_generadas:
                    cadenas_generadas.add(cadena_final)
            else:
                # Expandir el primer no terminal
                pos, nt = primer_no_terminal

                if nt in self.gramatica.P:
                    for produccion in self.gramatica.P[nt]:
                        nueva_forma = (
                                forma_sentencial[:pos] +
                                produccion +
                                forma_sentencial[pos + len(nt):]
                        )

                        # Evitar formas sentenciales muy largas
                        if len(nueva_forma) <= 100:
                            cola.append((nueva_forma, profundidad + 1))

        # Convertir a lista y ordenar por longitud
        cadenas_lista = sorted(list(cadenas_generadas), key=lambda x: (len(x), x))
        return cadenas_lista[:n]

    def _encontrar_primer_no_terminal(self, forma: str) -> tuple:
        """
        Encuentra el primer no terminal en la forma sentencial.
        Retorna (posición, no_terminal) o None si no hay.
        """
        if not forma:
            return None

        i = 0
        while i < len(forma):
            # Buscar no terminales (más largos primero)
            for nt in sorted(self.gramatica.N, key=len, reverse=True):
                if forma[i:].startswith(nt):
                    return (i, nt)

            # Si no es no terminal, avanzar por el terminal o epsilon
            avanzado = False

            # Buscar terminales (más largos primero)
            for t in sorted(self.gramatica.T, key=len, reverse=True):
                if forma[i:].startswith(t):
                    i += len(t)
                    avanzado = True
                    break

            if not avanzado:
                # Verificar epsilon
                if forma[i] == 'ε':
                    i += 1
                else:
                    # Avanzar un carácter si no reconocemos nada
                    i += 1

        return None