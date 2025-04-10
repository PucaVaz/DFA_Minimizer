import collections
try:
    from src.afd.representacao import AFD
except ImportError:
    from ..afd.representacao import AFD

def parse_afd_arquivo(caminho_arquivo: str) -> AFD | None:
    """
    Lê um arquivo de definição de AFD no formato especificado,
    ignorando comentários (incluindo inline) e retorna um objeto AFD.

    Args:
        caminho_arquivo (str): O caminho para o arquivo .txt.

    Returns:
        Optional[AFD]: Um objeto AFD se a análise for bem-sucedida, None caso contrário.
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            linhas_raw = f.readlines()
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado em '{caminho_arquivo}'")
        return None
    except Exception as e:
        print(f"ERRO: Não foi possível ler o arquivo '{caminho_arquivo}': {e}")
        return None

    alfabeto = None
    estados = set() 
    inicial = None
    finais = None
    transicoes_temp = [] 
    secao_atual = None   

    num_linha = 0
    for linha_raw in linhas_raw:
        num_linha += 1
        linha_limpa = linha_raw.split('#', 1)[0].strip()

        if not linha_limpa:
            continue

        linha_lower = linha_limpa.lower()

        if linha_lower.startswith("alfabeto:"):
            if alfabeto is not None:
                print(f"AVISO (Linha {num_linha}): Seção 'alfabeto' redefinida.")
            partes = linha_limpa.split(":", 1)
            if len(partes) == 2:
                alfabeto = set(val.strip() for val in partes[1].split(',') if val.strip())
            else:
                 print(f"AVISO (Linha {num_linha}): Formato inválido para 'alfabeto:'. Ignorando linha.")
            secao_atual = None 

        elif linha_lower.startswith("estados:"):
            partes = linha_limpa.split(":", 1)
            if len(partes) == 2:
                 estados_declarados = set(val.strip() for val in partes[1].split(',') if val.strip())
                 estados.update(estados_declarados)
            else:
                 print(f"AVISO (Linha {num_linha}): Formato inválido para 'estados:'. Ignorando linha.")
            secao_atual = None

        elif linha_lower.startswith("inicial:"):
            if inicial is not None:
                 print(f"AVISO (Linha {num_linha}): Estado 'inicial' redefinido.")
            partes = linha_limpa.split(":", 1)
            if len(partes) == 2:
                 inicial = partes[1].strip()
            else:
                 print(f"AVISO (Linha {num_linha}): Formato inválido para 'inicial:'. Ignorando linha.")
            secao_atual = None

        elif linha_lower.startswith("finais:"):
            if finais is not None:
                 print(f"AVISO (Linha {num_linha}): Seção 'finais' redefinida.")
            partes = linha_limpa.split(":", 1)
            if len(partes) == 2:
                 finais = set(val.strip() for val in partes[1].split(',') if val.strip())
            else:
                 print(f"AVISO (Linha {num_linha}): Formato inválido para 'finais:'. Ignorando linha.")
            secao_atual = None

        elif linha_lower == "transicoes":
            secao_atual = "transicoes"

        elif secao_atual == "transicoes":
            partes = [p.strip() for p in linha_limpa.split(',')]
            if len(partes) == 3:
                origem, destino, simbolo = partes
                if origem and destino and simbolo:
                    transicoes_temp.append((origem, destino, simbolo))
                    estados.add(origem)
                    estados.add(destino)
                else:
                    print(f"AVISO (Linha {num_linha}): Linha de transição com partes vazias ignorada: '{linha_limpa}'")
            else:
                print(f"AVISO (Linha {num_linha}): Linha de transição mal formada (não 3 partes separadas por vírgula) ignorada: '{linha_limpa}'")
        else:
             print(f"AVISO (Linha {num_linha}): Linha ignorada fora de seção conhecida: '{linha_limpa}'")

    if alfabeto is None:
        print("ERRO: Seção 'alfabeto:' não encontrada ou inválida no arquivo.")
        return None
    if inicial is None:
        print("ERRO: Seção 'inicial:' não encontrada ou inválida no arquivo.")
        return None
    if finais is None: 
        print("AVISO: Seção 'finais:' não encontrada ou inválida. Assumindo nenhum estado final.")
        finais = set() 
    if not transicoes_temp and secao_atual != "transicoes": 
         print("AVISO: Seção 'transicoes' não encontrada ou vazia.")

    transicoes_final = collections.defaultdict(dict)
    for origem, destino, simbolo in transicoes_temp:
        if simbolo not in alfabeto:
             print(f"AVISO: Símbolo '{simbolo}' na transição '{origem}->{destino}' não está no alfabeto declarado {alfabeto}. Verifique o arquivo ou adicione o símbolo.")


        if origem in transicoes_final and simbolo in transicoes_final[origem]:
            if transicoes_final[origem][simbolo] != destino:
                 print(f"AVISO: Transição não determinística ou redefinida para ({origem}, {simbolo}). Usando a última encontrada: -> {destino} (anterior era -> {transicoes_final[origem][simbolo]})")
            # else: # Ignorar entradas duplicadas
            #    pass
        transicoes_final[origem][simbolo] = destino

    # Converter defaultdict para dict para o objeto AFD
    transicoes_final_dict = dict(transicoes_final)

    if not estados:
        print("ERRO: Nenhum estado definido (nem declarado, nem encontrado em transições).")
        return None
    if inicial not in estados:
        print(f"ERRO: Estado inicial declarado '{inicial}' não pertence ao conjunto final de estados {estados} (verifique declarações e transições).")
        return None
    finais_invalidos = finais - estados
    if finais_invalidos:
        print(f"ERRO: Estados finais declarados {finais_invalidos} não pertencem ao conjunto final de estados {estados}.")
        return None # Ou seja, falhar estritamente

    try:
        return AFD(alfabeto, estados, inicial, finais, transicoes_final_dict)
    except Exception as e:
        print(f"ERRO: Falha ao instanciar o objeto AFD: {e}")
        return None