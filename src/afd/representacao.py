class AFD:
    def __init__(self, alfabeto, estados, inicial, finais, transicoes):
        self.alfabeto = set(alfabeto)
        self.estados = set(estados)
        self.inicial = inicial
        self.finais = set(finais)
        self.transicoes = transicoes
        
    def __str__(self):
        transicoes_str = "\n".join([f"{estado}: {transicao}" for estado, transicao in self.transicoes.items()])
        return f"AFD(alfabeto={self.alfabeto}, estados={self.estados}, inicial={self.inicial}, finais={self.finais}, transicoes={transicoes_str})"
    
    def __repr__(self):
        return f"AFD(inicial='{self.inicial}', estados={len(self.estados)}, finais={len(self.finais)})"
    