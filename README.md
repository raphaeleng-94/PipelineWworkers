Books to Scrape - Projeto de Web Scraping

Este projeto é um web scraper que extrai informações de livros do site Books to Scrape e armazena os dados em um banco de dados PostgreSQL. Ele usa processamento paralelo para realizar o scraping de várias páginas simultaneamente de maneira eficiente.

Funcionalidades:
Web scraping de informações sobre livros, incluindo:
Título
Classificação
Categoria
Preço
Status de estoque

Processamento paralelo usando ThreadPoolExecutor
Integração com banco de dados PostgreSQL
Logging com integração ao Logfire
Configuração de variáveis de ambiente
Tratamento de erros e logging

Pré-requisitos:
Python 3.x
Banco de dados PostgreSQL
Pacotes Python necessários (veja requirements.txt)

Instalação:

Clone o repositório:
bash
Copiar
Editar
git clone <repository-url>
cd <repository-name>

Instale os pacotes necessários:
bash
Copiar
Editar
pip install -r requirements.txt

Configure suas variáveis de ambiente em um arquivo .env:
env
Copiar
Editar
POSTGRES_USER=seu_usuario  
POSTGRES_PASSWORD=sua_senha  
POSTGRES_DB=nome_do_seu_banco  
POSTGRES_HOST=seu_host  
POSTGRES_PORT=sua_porta  

Estrutura do Projeto:
main.py: Script principal contendo a lógica de web scraping
banco.py: Modelos de banco de dados e configuração
.env: Variáveis de ambiente (não incluídas no repositório)
requirements.txt: Dependências do projeto

Como Usar:
Certifique-se de que o banco de dados PostgreSQL está em execução e acessível
Execute o script principal:
bash
Copiar
Editar
python main.py

O script irá:

Criar as tabelas necessárias no banco de dados (se ainda não existirem)
Realizar o scraping de todas as páginas do site Books to Scrape
Processar os dados em paralelo usando múltiplas threads
Salvar os resultados no banco de dados PostgreSQL
Esquema do Banco de Dados

O script cria uma tabela chamada estoque_livros com as seguintes colunas:

titulo (Título)
classificacao (Classificação)
categoria (Categoria)
preco (Preço)
estoque (Status de estoque)
timestamp (Hora de criação do registro)

Logging:
O projeto usa o Logfire para logging, fornecendo:

Rastreamento de requisições
Logging de queries do SQLAlchemy
Rastreamento de erros
Monitoramento de desempenho

Desempenho:
O script usa ThreadPoolExecutor com 8 workers para processar múltiplas páginas simultaneamente, o que melhora significativamente a velocidade de scraping em comparação com o processamento sequencial.

Tratamento de Erros:
O script inclui um tratamento de erros abrangente para:

Requisições de rede
Operações de banco de dados
Parsing de dados
Execução de threads

Contribuição:
Sinta-se à vontade para enviar problemas e sugestões de melhorias!

Licença:
Este projeto está sob a licença MIT.

## Raphael Amorim
