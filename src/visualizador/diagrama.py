import graphviz
import os
from src.afd.representacao import AFD

def gerar_diagrama_afd(afd: AFD, nome_arquivo_base: str):
    dot = graphviz.Digraph(comment='Diagrama AFD', format='png')
    dot.attr(rankdir='LR')
    dot.attr(size='8,8')
    dot.attr(dpi='300')
    dot.attr(concentrate='true')
    dot.attr(ordering='in')
    dot.node('__start__', shape='point', style='invis')

    def format_state(state):
        if isinstance(state, frozenset):
            return ','.join(sorted(str(s) for s in state))
        return str(state)

    initial_state_str = format_state(afd.inicial)
    dot.edge('__start__', initial_state_str)

    for estado in afd.estados:
        estado_str = format_state(estado)
        if estado in afd.finais:
            dot.node(estado_str, shape='doublecircle')
        else:
            dot.node(estado_str, shape='circle')

    for origem, transicoes_simbolo in afd.transicoes.items():
        origem_str = format_state(origem)
        for simbolo, destino in transicoes_simbolo.items():
            destino_str = format_state(destino)
            dot.edge(origem_str, destino_str, label=str(simbolo))

    try:
        output_path = os.path.abspath(nome_arquivo_base)
        dot.render(output_path, view=False, cleanup=True)
        print(f"\nDiagrama do AFD salvo como '{output_path}.png'")
    except graphviz.backend.execute.ExecutableNotFound:
        print("\nErro: 'dot' command not found.")
        print("Graphviz não está instalado ou não está no PATH do sistema.")
        print("Instale Graphviz de http://www.graphviz.org/download/")
    except Exception as e:
        print(f"\nErro ao gerar o diagrama com Graphviz: {e}")