from typing import Dict, List, Set

class Gramatica:
    def __init__(self, no_terminales: Set[str], terminales: Set[str],
                 producciones: Dict[str, List[str]], simbolo_inicial: str, tipo: str):
        self.N = no_terminales
        self.T = terminales
        self.P = producciones
        self.S = simbolo_inicial
        self.tipo = tipo

    def to_dict(self):
        return {
            'no_terminales': list(self.N),
            'terminales': list(self.T),
            'producciones': self.P,
            'simbolo_inicial': self.S,
            'tipo': self.tipo
        }

    @staticmethod
    def from_dict(data):
        return Gramatica(
            set(data['no_terminales']),
            set(data['terminales']),
            data['producciones'],
            data['simbolo_inicial'],
            data['tipo']
        )
