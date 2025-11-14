class ArbolDerivacion:
    def __init__(self, simbolo: str):
        self.simbolo = simbolo
        self.hijos = []

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

    def to_dict(self):
        return {
            'simbolo': self.simbolo,
            'hijos': [hijo.to_dict() for hijo in self.hijos]
        }

    def to_text(self, nivel=0):
        resultado = "  " * nivel + self.simbolo + "\n"
        for hijo in self.hijos:
            resultado += hijo.to_text(nivel + 1)
        return resultado