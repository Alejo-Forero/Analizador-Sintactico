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
        # Manejar dos formatos de producciones
        producciones = data.get('producciones') or data.get('P')
        
        # Si las producciones están en formato de lista ["S -> L", "S -> L T"]
        if isinstance(producciones, list):
            producciones_dict = {}
            for regla in producciones:
                if '->' in regla:
                    partes = regla.split('->')
                    no_terminal = partes[0].strip()
                    lado_derecho = partes[1].strip()
                    
                    if no_terminal not in producciones_dict:
                        producciones_dict[no_terminal] = []
                    producciones_dict[no_terminal].append(lado_derecho)
            producciones = producciones_dict
        
        # Manejar diferentes nombres de campos en el JSON
        no_terminales = set(data.get('no_terminales') or data.get('N', []))
        terminales = set(data.get('terminales') or data.get('T', []))
        simbolo_inicial = data.get('simbolo_inicial') or data.get('S')
        tipo = str(data.get('tipo') or data.get('type', ''))
        
        return Gramatica(
            no_terminales,
            terminales,
            producciones,
            simbolo_inicial,
            tipo
        )
