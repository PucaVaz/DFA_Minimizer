from typing import Set, List, Optional
from collections import deque

try:
    from src.afd.representacao import AFD
except ImportError:
    from ..afd.representacao import AFD


def _encontrar_estados_alcancaveis(afd: AFD) -> Set[str]:
    if not afd.estados or afd.inicial not in afd.estados: return set()
    alcancaveis = set(); fila = deque([afd.inicial]); alcancaveis.add(afd.inicial)
    while fila:
        estado_atual = fila.popleft()
        if estado_atual in afd.transicoes:
            for simbolo in afd.alfabeto:
                proximo_estado = afd.transicoes.get(estado_atual, {}).get(simbolo)
                if proximo_estado is not None and proximo_estado not in alcancaveis:
                    if proximo_estado in afd.estados:
                        alcancaveis.add(proximo_estado); fila.append(proximo_estado)
    return alcancaveis



def _formatar_tabela_marcacao(estados: List[str], marked_pairs: Set[frozenset], passo_num: Optional[int] = 0) -> str:
    output = []
    if passo_num == 0: output.append("Passo 0: Marcação inicial (Final vs Não-Final)")
    else: output.append(f"Estado da Tabela após Passo {passo_num}:")
    marked_list = sorted([tuple(sorted(list(p))) for p in marked_pairs])
    output.append(" Pares Marcados (Distinguíveis):")
    if not marked_list: output.append("  Nenhum")
    else: pairs_str = ", ".join([f"{{{p[0]},{p[1]}}}" for p in marked_list]); output.append(f"  {pairs_str}")
    return "\n".join(output)

def _formatar_novos_marcados(passo_num: int, newly_marked: Set[frozenset]) -> str:
    output = []
    output.append(f"\nPasso {passo_num}: Novos pares marcados como distinguíveis")
    if not newly_marked: output.append("  Nenhum")
    else:
        sorted_new = sorted([tuple(sorted(list(p))) for p in newly_marked])
        for p_tuple in sorted_new: output.append(f"  - {{{p_tuple[0]},{p_tuple[1]}}}")
    return "\n".join(output)