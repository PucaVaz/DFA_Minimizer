import argparse
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.afd.representacao import AFD
    from src.minimizador.parser import parse_afd_arquivo
    from src.minimizador.validador import validar_afd

    from src.minimizador.algoritmo import minimizar_afd
    from src.visualizador.diagrama import gerar_diagrama_afd
except ImportError as e:
    print(f"Erro fatal: Falha ao importar módulos do projeto: {e}", file=sys.stderr)
    print("Verifique se o script está sendo executado corretamente e a estrutura 'src' existe.", file=sys.stderr)
    sys.exit(1) 

def run_minimizer_cli(input_filepath: str, output_basename: str):
    """
    Executes the full DFA minimization pipeline for the CLI.

    Args:
        input_filepath (str): Path to the input .txt file defining the AFD.
        output_basename (str): Base name for the output diagram file (e.g., 'output/minimized').
                               The extension (.png) will be added automatically.
    """
    print("-" * 30)
    print(">>> Minimizador de AFD (Versão CLI) <<<")
    print("-" * 30)

    # 1. Parse Input File
    print(f"\n[1] Analisando arquivo de entrada: '{input_filepath}'...")
    original_afd = parse_afd_arquivo(input_filepath)

    if original_afd is None:
        print("\nERRO FATAL: Falha ao analisar o arquivo de entrada. Verifique o formato.")
        sys.exit(1)
    else:
        print("--> Análise concluída com sucesso.")
        # print("AFD Original Lido:") # Optional: mostrar mais detalhes
        # print(original_afd)

    # 2. Validate AFD
    print("\n[2] Validando o AFD...")
    is_valido, mensagens_validacao, _ = validar_afd(original_afd)

    if mensagens_validacao:
        print("--> Mensagens da Validação:")
        for msg in mensagens_validacao:
            print(f"    - {msg}")
    else:
        print("--> Nenhuma mensagem da validação.")

    if not is_valido:
        print("\nERRO FATAL: O AFD fornecido é inválido (contém ERROS na validação). Não é possível minimizar.")
        sys.exit(1)
    else:
        if any("ERRO:" in msg for msg in mensagens_validacao):
             print("\nERRO FATAL: O AFD contém ERROS na validação. Não é possível minimizar.")
             sys.exit(1)
        elif any("AVISO:" in msg for msg in mensagens_validacao):
             print("--> Validação OK (com AVISOS). Prosseguindo com a minimização...")
        else:
             print("--> Validação OK. AFD é válido.")


    # 3. Minimizar AFD (Consumindo o gerador e imprimindo etapas)
    print("\n[3] Minimizando o AFD...")
    minimized_afd_result = None
    error_occurred = False

    # A versão geradora de 'minimizar_afd' lida com a impressão interna via yield/callback padrão
    # Percorremos o gerador principalmente para obter o resultado final ou capturar erros gerados.
    try:
        # Chame o gerador diretamente; ele usa print por padrão se nenhum callback for passado.
        # Ainda precisamos iterar sobre ele para conduzir o processo e obter o resultado.
        for step_info in minimizar_afd(original_afd):
             # O próprio gerador está imprimindo etapas. Apenas procuramos o resultado/erro.
            if isinstance(step_info, dict):
                if step_info["type"] == "result":
                    minimized_afd_result = step_info["data"]
                elif step_info["type"] == "error":
                    # O gerador pode gerar uma mensagem de erro antes de parar
                    print(f"ERRO durante minimização: {step_info.get('message', 'Erro desconhecido')}")
                    error_occurred = True
                    break # Pare o processamento se o gerador gerar um erro
            # else: # Lidar com yields não-dict se houver (não deve acontecer com o design atual)
            #    print(str(step_info)) # Impressão de fallback

    except Exception as e:
        print(f"\nERRO INESPERADO durante a minimização: {e}")
        error_occurred = True

    if error_occurred or minimized_afd_result is None:
        print("\nERRO FATAL: Falha na execução do algoritmo de minimização.")
        sys.exit(1)
    else:
        print("\n--> Minimização concluída com sucesso.")
        print("AFD Minimizado:")
        print(minimized_afd_result) # Print using AFD's __str__

    # 4. Generate Diagram
    print(f"\n[4] Gerando diagrama do AFD minimizado em '{output_basename}.png'...")
    # Ensure output directory exists if specified in the basename
    output_dir = os.path.dirname(output_basename)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"--> Diretório de saída criado: '{output_dir}'")
        except OSError as e:
            print(f"\nERRO FATAL: Não foi possível criar o diretório de saída '{output_dir}': {e}")
            sys.exit(1)

    try:
        gerar_diagrama_afd(minimized_afd_result, output_basename)
    except Exception as e:
        print(f"\nERRO FATAL: Falha inesperada ao gerar o diagrama: {e}")
        sys.exit(1)

    print("\n[5] Processo concluído com sucesso!")
    print("-" * 30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Minimiza um Autômato Finito Determinístico (AFD) a partir de um arquivo de definição.")

    parser.add_argument(
        "input_file",
        metavar="ARQUIVO_ENTRADA",
        type=str,
        help="Caminho para o arquivo .txt contendo a definição do AFD."
    )

    parser.add_argument(
        "output_basename",
        metavar="NOME_BASE_SAIDA",
        type=str,
        help="Nome base para o arquivo de diagrama de saída (sem extensão). Ex: 'output/meu_afd_min' gerará 'output/meu_afd_min.png'."
    )

    args = parser.parse_args()

    run_minimizer_cli(args.input_file, args.output_basename)