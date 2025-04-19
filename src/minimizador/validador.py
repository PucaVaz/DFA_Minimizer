import collections
from typing import Tuple, List, Set, Optional

try:
    from src.afd.representacao import AFD
except ImportError:
    from ..afd.representacao import AFD


def _verificar_consistencia(afd: AFD, mensagens: List[str]):
    """Verifica consistência interna dos componentes do AFD."""
    erros_consistencia = 0

    # 1. Estado inicial pertence ao conjunto de estados?
    if afd.inicial not in afd.estados:
        mensagens.append(f"ERRO: Estado inicial '{afd.inicial}' não está no conjunto de estados {afd.estados}.")
        erros_consistencia += 1

    # 2. Estados finais pertencem ao conjunto de estados?
    estados_finais_invalidos = afd.finais - afd.estados
    if estados_finais_invalidos:
        mensagens.append(f"ERRO: Estados finais {estados_finais_invalidos} não estão no conjunto de estados {afd.estados}.")
        erros_consistencia += 1

    # 3. Transições usam apenas estados e símbolos declarados?
    for origem, transicoes_simbolo in afd.transicoes.items():
        # 3a. Origem pertence aos estados?
        if origem not in afd.estados:
            mensagens.append(f"ERRO: Estado de origem '{origem}' em transições não está no conjunto de estados.")
            erros_consistencia += 1 # Contar apenas uma vez por estado de origem inválido

        for simbolo, destino in transicoes_simbolo.items():
            # 3b. Símbolo pertence ao alfabeto?
            if simbolo not in afd.alfabeto:
                mensagens.append(f"ERRO: Símbolo '{simbolo}' na transição de '{origem}'->'{destino}' não está no alfabeto {afd.alfabeto}.")
                erros_consistencia += 1
            # 3c. Destino pertence aos estados?
            if destino not in afd.estados:
                 mensagens.append(f"ERRO: Estado de destino '{destino}' na transição de '{origem}' por '{simbolo}' não está no conjunto de estados.")
                 erros_consistencia += 1

    return erros_consistencia == 0


def _verificar_determinismo(afd: AFD, mensagens: List[str]):
    """Verifica se o AFD é completo (determinístico)."""
    determinismo_ok = True
    for estado in afd.estados:
        for simbolo in afd.alfabeto:
            if estado not in afd.transicoes or simbolo not in afd.transicoes.get(estado, {}):
                mensagens.append(f"ERRO: Transição ausente para o estado '{estado}' com o símbolo '{simbolo}'. AFD não é completo.")
                determinismo_ok = False

    return determinismo_ok


def _verificar_alcancabilidade(afd: AFD, mensagens: List[str]) -> Set[str]:
    """Encontra estados alcançáveis via BFS e reporta inalcançáveis."""
    if not afd.estados:
        return set()
    if afd.inicial not in afd.estados:
        # Erro já pego pela consistencia, não há o que alcançar
        return set()

    alcancaveis = set()
    fila = collections.deque([afd.inicial])
    alcancaveis.add(afd.inicial)

    while fila:
        estado_atual = fila.popleft()

        # Verifica transições a partir do estado atual
        if estado_atual in afd.transicoes:
            for simbolo in afd.alfabeto:
                # Ver no nosso hashmap caso o determinismo não tenham sido chegado
                proximo_estado = afd.transicoes.get(estado_atual, {}).get(simbolo)

                # Se a transição existe e leva a um estado ainda não visitado
                if proximo_estado is not None and proximo_estado not in alcancaveis:
                    # Verifica se o próximo estado é válido (deve ser, se consistencia passou)
                    if proximo_estado in afd.estados:
                        alcancaveis.add(proximo_estado)
                        fila.append(proximo_estado)
                    # else: # Caso extremo onde transição leva a estado não declarado
                    #    mensagens.append(f"AVISO: Transição de '{estado_atual}' com '{simbolo}' leva a estado '{proximo_estado}' fora do conjunto de estados declarados.")

    # Reportar estados inalcançáveis (se houver)
    estados_inalcancaveis = afd.estados - alcancaveis
    if estados_inalcancaveis:
        mensagens.append(f"AVISO: Os seguintes estados são inalcançáveis a partir de '{afd.inicial}': {estados_inalcancaveis}.")

    return alcancaveis


# --- Função Principal de Validação ---

def validar_afd(afd: AFD) -> Tuple[bool, List[str], Optional[Set[str]]]:
    """
    Valida um objeto AFD verificando consistência, determinismo e alcançabilidade.

    Args:
        afd (AFD): O objeto AFD a ser validado.

    Returns:
        Tuple[bool, List[str], Optional[Set[str]]]:
        - bool: True se o AFD for considerado válido (consistente e determinístico), False caso contrário.
        - List[str]: Uma lista de mensagens de erro ou aviso encontradas.
        - Optional[Set[str]]: O conjunto de estados alcançáveis a partir do estado inicial,
                               ou None se a validação falhar criticamente antes da alcançabilidade.
    """
    mensagens = []
    is_valido = True
    estados_alcancaveis = None

    # 0. Checagem básica de objeto vazio
    if not afd or not afd.estados or not afd.alfabeto or not afd.inicial:
        mensagens.append("ERRO: Objeto AFD está vazio ou incompleto (sem estados, alfabeto ou estado inicial).")
        return False, mensagens, None

    # 1. Verificar Consistência
    if not _verificar_consistencia(afd, mensagens):
        is_valido = False
        # Se a consistência falha gravemente (e.g., estado inicial inválido),
        # outras verificações podem não fazer sentido. Pode retornar aqui se desejar.
        # return False, mensagens, None

    # 2. Verificar Determinismo (Completude)
    if not _verificar_determinismo(afd, mensagens):
        is_valido = False

    # 3. Verificar Alcançabilidade (mesmo se inválido, pode ser informativo)
    # Só faz sentido calcular se o estado inicial for válido
    if afd.inicial in afd.estados:
         estados_alcancaveis = _verificar_alcancabilidade(afd, mensagens)
         # Checa se o estado inicial é alcançável (deve ser, por definição, se não houver bugs)
         # Mas se o conjunto de estados estiver vazio, pode dar problema.
         if not estados_alcancaveis and afd.estados:
              # Caso estranho, talvez inicial não esteja em estados após tudo?
              mensagens.append(f"ERRO: Não foi possível determinar estados alcançáveis a partir de '{afd.inicial}'.")
              is_valido = False # Define como inválido se não consegue nem alcançar o inicial

    # Se chegou aqui, retorna o status e as mensagens acumuladas
    return is_valido, mensagens, estados_alcancaveis

# Exemplo de como usar (pode ser colocado em main.py ou em testes)
if __name__ == '__main__':
    # Criar um AFD de exemplo (válido)
    afd_valido = AFD(
        alfabeto={'0', '1'},
        estados={'q0', 'q1', 'q2'},
        inicial='q0',
        finais={'q2'},
        transicoes={
            'q0': {'0': 'q1', '1': 'q0'},
            'q1': {'0': 'q1', '1': 'q2'},
            'q2': {'0': 'q1', '1': 'q0'}
        }
    )
    valido, msgs, alcancaveis = validar_afd(afd_valido)
    print(f"AFD Válido: {valido}")
    print(f"Mensagens: {msgs}")
    print(f"Alcançáveis: {alcancaveis}")
    print("-" * 20)

    # Criar um AFD de exemplo (inválido - incompleto)
    afd_invalido_incompleto = AFD(
        alfabeto={'a', 'b'},
        estados={'S', 'A'},
        inicial='S',
        finais={'A'},
        transicoes={
            'S': {'a': 'A'} # Falta transição para 'b' em S e todas em A
        }
    )
    valido, msgs, alcancaveis = validar_afd(afd_invalido_incompleto)
    print(f"AFD Inválido (Incompleto): {valido}")
    print(f"Mensagens: {msgs}")
    print(f"Alcançáveis: {alcancaveis}")
    print("-" * 20)

     # Criar um AFD de exemplo (inválido - estado final não existe)
    afd_invalido_final = AFD(
        alfabeto={'a'},
        estados={'q0'},
        inicial='q0',
        finais={'q1'}, # q1 não está nos estados
        transicoes={
            'q0': {'a': 'q0'}
        }
    )
    valido, msgs, alcancaveis = validar_afd(afd_invalido_final)
    print(f"AFD Inválido (Final): {valido}")
    print(f"Mensagens: {msgs}")
    print(f"Alcançáveis: {alcancaveis}")
    print("-" * 20)

    # Criar um AFD de exemplo (aviso - inalcançável)
    afd_aviso_inalcancavel = AFD(
        alfabeto={'0'},
        estados={'q0', 'q1', 'q2'}, # q2 é inalcançável
        inicial='q0',
        finais={'q1'},
        transicoes={
            'q0': {'0': 'q1'},
            'q1': {'0': 'q0'},
            'q2': {'0': 'q2'} # Transição de q2, mas q2 não é alcançado
        }
    )
    valido, msgs, alcancaveis = validar_afd(afd_aviso_inalcancavel)
    print(f"AFD Válido (com aviso): {valido}")
    print(f"Mensagens: {msgs}")
    print(f"Alcançáveis: {alcancaveis}")
    print("-" * 20)
