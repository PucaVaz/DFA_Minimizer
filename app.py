import streamlit as st
import os
import sys
import tempfile 

project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from afd.representacao import AFD
    from minimizador.parser import parse_afd_arquivo
    from minimizador.validador import validar_afd
    from minimizador.algoritmo import minimizar_afd
    from visualizador.diagrama import gerar_diagrama_afd
except ImportError as e:
    st.error(f"Erro ao importar módulos do projeto: {e}")
    st.error(f"Verifique se o arquivo app.py está na raiz do projeto e a estrutura 'src' existe.")
    st.stop() 

st.set_page_config(page_title="Minimizador de AFD", layout="wide")

st.title("Minimizador de Autômatos Finitos Determinísticos (AFD)")
st.write("Carregue um arquivo .txt com a definição do AFD para validá-lo e minimizá-lo.")

uploaded_file = st.file_uploader("Escolha um arquivo .txt com a definição do AFD", type="txt")

status_placeholder = st.empty()
log_placeholder = st.empty()

diagram_container = st.container()

if uploaded_file is not None:
    if st.button("Processar AFD"):
        status_placeholder.empty()
        log_placeholder.empty()
        log_content = ""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding='utf-8') as tmp_file:
            tmp_file.write(uploaded_file.getvalue().decode("utf-8"))
            tmp_file_path = tmp_file.name

        try:
            # 1. Análise do arquivo de entrada
            st.info("1. Analisando arquivo de entrada...")
            original_afd = parse_afd_arquivo(tmp_file_path)

            if original_afd is None:
                status_placeholder.error("Falha ao analisar o arquivo. Verifique o formato e as mensagens de erro no console (se houver).")
                st.stop()
            else:
                st.success("Arquivo analisado com sucesso.")

            # 2. Validação
            st.info("2. Validando o AFD...")
            is_valido, mensagens_validacao, estados_alcancaveis = validar_afd(original_afd)

            if mensagens_validacao:
                 status_placeholder.warning("Mensagens da Validação:\n" + "\n".join(f"- {msg}" for msg in mensagens_validacao))
            else:
                 status_placeholder.success("Validação inicial OK (Consistência/Determinismo).")

            if not is_valido:
                status_placeholder.error("O AFD fornecido é inválido de acordo com as verificações de consistência e/ou determinismo. Não é possível minimizar.")
                st.stop()
            else:
                 st.success("AFD considerado válido para minimização.")
                 if estados_alcancaveis is not None:
                      st.info(f"Estados alcançáveis identificados: {sorted(list(estados_alcancaveis))}")

            # 3. Minimização
            st.info("3. Iniciando Minimização (Algoritmo Table-Filling)...")
            minimized_afd_result = None
            generator_finished = False

            for step_info in minimizar_afd(original_afd):
                 generator_finished = True
                 if isinstance(step_info, dict):
                     msg = step_info.get("message", "")
                     log_content += msg + "\n"
    
                     data = step_info.get("data")
                     if data and step_info.get("type") not in ["result", "error", "start"]:
                         if isinstance(data, (list, set)):
                              formatted_data = "\n".join(f"    {item}" for item in sorted(list(data)))
                         else:
                              formatted_data = str(data)
                         log_content += formatted_data + "\n"

                     if step_info["type"] == "result":
                         minimized_afd_result = data
                         log_content += "\nINFO: AFD Minimizado Construído.\n"
                     elif step_info["type"] == "error":
                         log_content += f"ERRO: {msg}\n"
                         status_placeholder.error(f"Erro durante a minimização: {msg}")

                 else:
                      log_content += str(step_info) + "\n"

            if not generator_finished:
                 status_placeholder.error("O algoritmo de minimização não produziu nenhum passo (verifique a implementação).")
                 st.stop()

            # 4. Geração e exibição dos diagramas
            if minimized_afd_result:
                st.success("Minimização concluída com sucesso!")
                st.info("4. Gerando diagramas do AFD original e minimizado...")

                output_dir = os.path.join(project_root, "data", "output")
                os.makedirs(output_dir, exist_ok=True)
                diagram_original_basename = os.path.join(output_dir, os.path.splitext(uploaded_file.name)[0] + "_original")
                diagram_minimizado_basename = os.path.join(output_dir, os.path.splitext(uploaded_file.name)[0] + "_minimizado")

                try:
                    # Geração do diagrama do AFD original
                    gerar_diagrama_afd(original_afd, diagram_original_basename)
                    diagram_original_path = diagram_original_basename + ".png"
                    
                    # Geração do diagrama do AFD minimizado
                    gerar_diagrama_afd(minimized_afd_result, diagram_minimizado_basename)
                    diagram_minimizado_path = diagram_minimizado_basename + ".png"

                    # Exibição do log da minimização
                    st.markdown("### Log da Minimização")
                    st.text_area("", log_content, height=400)

                    # Exibição dos diagramas 
                    if os.path.exists(diagram_original_path) and os.path.exists(diagram_minimizado_path):
                        st.markdown("### Diagramas do AFD")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(diagram_original_path, caption="Diagrama do AFD Original", use_container_width=True)
                        with col2:
                            st.image(diagram_minimizado_path, caption="Diagrama do AFD Minimizado", use_container_width=True)
                    else:
                        status_placeholder.warning("Um ou mais diagramas não foram gerados corretamente.")

                except Exception as e:
                    status_placeholder.error(f"Falha ao gerar ou exibir os diagramas: {e}")
                    st.error("Certifique-se que o Graphviz está instalado e acessível no PATH do sistema.")
            else:
                 if "ERRO:" not in log_content:
                     status_placeholder.error("Falha na minimização. Verifique o log.")

        finally:
            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path) 