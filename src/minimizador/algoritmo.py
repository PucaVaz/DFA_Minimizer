import itertools
from collections import defaultdict
from typing import Generator, Any,Dict

try:
    from src.afd.representacao import AFD
except ImportError:
    from ..afd.representacao import AFD

from .helpers import _encontrar_estados_alcancaveis, _formatar_tabela_marcacao, _formatar_novos_marcados

class DSU:
    def __init__(self, items):
        self.parent = {item: item for item in items}
    def find(self, item):
        if self.parent[item] == item: return item
        self.parent[item] = self.find(self.parent[item])
        return self.parent[item]
    def union(self, item1, item2):
        root1, root2 = self.find(item1), self.find(item2)
        if root1 != root2: self.parent[root1] = root2


def minimizar_afd(afd_original: AFD) -> Generator[Dict[str, Any], None, None]:
    """
    Minimiza um dado AFD usando o algoritmo de Table-Filling, produzindo
    output passo-a-passo através de 'yield'.

    Args:
        afd_original (AFD): O objeto AFD original a ser minimizado (assume-se validado).

    Yields:
        Dict[str, Any]: Dicionários contendo informações sobre cada passo ou o resultado final.
                       Ex: {'type': 'info', 'message': '...'}
                           {'type': 'step_table', 'pass': 0, 'data': '...'}
                           {'type': 'step_update', 'pass': 1, 'data': '...'}
                           {'type': 'result', 'data': <AFD object>}
                           {'type': 'error', 'message': '...'}
    """
    # --- Setup ---
    estados_originais = afd_original.estados
    alfabeto = afd_original.alfabeto
    transicoes = afd_original.transicoes
    inicial = afd_original.inicial
    finais_originais = afd_original.finais

    yield {"type": "info", "message": "INFO: Encontrando estados alcançáveis..."}
    estados_alcancaveis = _encontrar_estados_alcancaveis(afd_original)

    if not estados_alcancaveis:
        yield {"type": "error", "message": "ERRO: Nenhum estado alcançável encontrado. Não é possível minimizar."}
        return # Stop the generator
    if inicial not in estados_alcancaveis:
         yield {"type": "error", "message": f"ERRO: Estado inicial '{inicial}' não é alcançável."}
         return

    yield {"type": "info", "message": f"INFO: Trabalhando com {len(estados_alcancaveis)} estados alcançáveis: {sorted(list(estados_alcancaveis))}"}
    if len(estados_alcancaveis) < len(estados_originais):
        yield {"type": "info", "message": f"INFO: Estados inalcançáveis ignorados: {estados_originais - estados_alcancaveis}"}

    estados_lista_ordenada = sorted(list(estados_alcancaveis))
    state_pairs = list(itertools.combinations(estados_lista_ordenada, 2))
    finais_alcancaveis = finais_originais.intersection(estados_alcancaveis)
    non_finais_alcancaveis = estados_alcancaveis - finais_alcancaveis
    marked_pairs = set()

    # --- Part 1: Table Filling ---
    yield {"type": "info", "message": "\n--- Minimização Passo-a-Passo ---"}

    # 1. Inicialização
    for p in finais_alcancaveis:
        for q in non_finais_alcancaveis:
             if p != q: marked_pairs.add(frozenset({p, q}))

    # Yield o estado inicial da tabela 
    yield {"type": "step_table", "pass": 0, "data": _formatar_tabela_marcacao(estados_lista_ordenada, marked_pairs, passo_num=0)}

    # 2. Iteração
    passo = 1
    while True:
        newly_marked = set()
        for p, q in state_pairs:
            pair = frozenset({p, q})
            if pair in marked_pairs: continue

            for simbolo in alfabeto:
                next_p = transicoes.get(p, {}).get(simbolo)
                next_q = transicoes.get(q, {}).get(simbolo)
                if next_p is None or next_q is None: continue 

                if next_p != next_q:
                    next_pair = frozenset({next_p, next_q})
                    if next_pair in marked_pairs:
                        newly_marked.add(pair)
                        break

        if not newly_marked:
            yield {"type": "info", "message": f"\nPasso {passo}: Nenhuma nova marcação. Algoritmo de marcação concluído."}
            break

        yield {"type": "step_update", "pass": passo, "data": _formatar_novos_marcados(passo, newly_marked)}

        marked_pairs.update(newly_marked)
        # Yield o estado completo da tabela novamente
        yield {"type": "step_table", "pass": passo, "data": _formatar_tabela_marcacao(estados_lista_ordenada, marked_pairs, passo_num=passo)}
        passo += 1

    yield {"type": "info", "message": "----------------------------------"}
    yield {"type": "info", "message": "\nConstruindo AFD minimizado..."}

    # --- Part 2: Construção do AFD Minimizado ---
    dsu = DSU(estados_alcancaveis)
    for p, q in state_pairs:
        if frozenset({p, q}) not in marked_pairs: dsu.union(p, q)

    equivalence_classes = defaultdict(set)
    for estado in estados_alcancaveis:
        equivalence_classes[dsu.find(estado)].add(estado)

    min_estados_fs = {frozenset(group) for group in equivalence_classes.values()}

    if not min_estados_fs:
        yield {"type": "error", "message": "ERRO: Nenhuma classe de equivalência encontrada."}
        return

    state_to_class_fs = {orig: fs for fs in min_estados_fs for orig in fs}
    min_inicial_fs = state_to_class_fs[inicial]
    min_finais_fs = {fs for fs in min_estados_fs if any(s in finais_alcancaveis for s in fs)}
    min_transicoes = defaultdict(dict)
    for fs_class in min_estados_fs:
        rep = next(iter(fs_class))
        for simbolo in alfabeto:
            orig_dest = transicoes.get(rep, {}).get(simbolo)
            if orig_dest is not None and orig_dest in estados_alcancaveis:
                 min_transicoes[fs_class][simbolo] = state_to_class_fs[orig_dest]

    minimized_afd = AFD(
        alfabeto=alfabeto, estados=min_estados_fs, inicial=min_inicial_fs,
        finais=min_finais_fs, transicoes=dict(min_transicoes)
    )
    yield {"type": "info", "message": "INFO: Construção do AFD minimizado concluída."}
    yield {"type": "result", "data": minimized_afd}


if __name__ == '__main__':
    afd_para_minimizar = AFD(
        alfabeto={'a', 'b'},
        estados={'A', 'B', 'C', 'D', 'E', 'F'},
        inicial='A',
        finais={'C', 'D'},
        transicoes={
            'A': {'a': 'B', 'b': 'F'},
            'B': {'a': 'E', 'b': 'C'},
            'C': {'a': 'E', 'b': 'C'}, # Final
            'D': {'a': 'E', 'b': 'D'}, # Final (Equiv C)
            'E': {'a': 'E', 'b': 'F'}, # Equiv F
            'F': {'a': 'F', 'b': 'F'}  # Equiv E
        }
    )

    print("Executando minimização com callback=print (padrão):")
    min_afd = minimizar_afd(afd_para_minimizar) 
    if min_afd:
        print("\nAFD Minimizado Resultante:")
        print(min_afd)
    else:
        print("\nMinimização falhou.")

    print("\n" + "="*30 + "\n")

    log_mensagens = []
    def coletar_log(mensagem):
        log_mensagens.append(str(mensagem))

    print("Executando minimização com callback customizado (coletar_log):")
    min_afd_2 = minimizar_afd(afd_para_minimizar, callback=coletar_log)

    print("\n--- Log Coletado ---")
    for msg in log_mensagens:
        print(msg)
    print("--------------------")

    if min_afd_2:
        print("\nAFD Minimizado Resultante (mesmo de antes):")
        print(min_afd_2)
    else:
        print("\nMinimização falhou.")