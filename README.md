# Minimizador de Autômatos Finitos Determinísticos (AFD)

Este projeto implementa um minimizador de Autômatos Finitos Determinísticos (AFD) com interface gráfica usando Streamlit.

## Descrição

O Minimizador de AFD é uma ferramenta que permite:
- Carregar um AFD a partir de um arquivo de texto
- Validar a consistência e o determinismo do autômato
- Minimizar o AFD utilizando o algoritmo de Table-Filling (Preenchimento de Tabela)
- Visualizar os diagramas dos AFDs original e minimizado

## Estrutura do Projeto

```
DFA_Minimizer/
│
├── app.py                # Aplicação principal (interface Streamlit)
├── src/                  # Código-fonte do projeto
│   ├── afd/              # Módulo para representação de AFDs
│   ├── minimizador/      # Implementação do algoritmo de minimização
│   └── visualizador/     # Módulo para geração de diagramas
│
└── data/                 # Diretório para arquivos de entrada/saída
```

## Requisitos

- Python 3.12+
- Streamlit
- Graphviz (instalado no sistema)
- Outras dependências listadas em `requirements.txt`

## Como Executar

1. Clone o repositório:
   ```
   # Atualmente, o repositório está como privado
   git clone https://github.com/PucaVaz/DFA_Minimizer.git
   cd DFA_Minimizer
   ```

2. Instale as dependências (recomendável usar ambiente virtual):
   ```
   python -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   pip install -r requirements.txt  # Se existir
   pip install streamlit
   ```

3. Execute a aplicação:
   ```
   python -m streamlit run app.py
   ```

4. Acesse a interface web através do navegador (normalmente em http://localhost:8501)

## Como Usar

1. Carregue um arquivo .txt contendo a definição do seu AFD
2. Clique em "Processar AFD"
3. Acompanhe o processo de validação e minimização
4. Visualize os diagramas dos AFDs original e minimizado

## Formato do Arquivo de Entrada

O arquivo de entrada deve seguir o formato adequado para definição de AFDs.
Consulte a documentação específica para mais detalhes sobre o formato aceito.

## Autores

- Pedro Luca Vaz Matias 
- Joao Vittor de Araujo Alves

## Licença
Este projeto está licenciado sob a GNU General Public License v3.0
