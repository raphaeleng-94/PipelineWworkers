import requests
from bs4 import BeautifulSoup
import os
import time
import logging
import psycopg2
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from sqlalchemy import text
from dotenv import load_dotenv
from logging import basicConfig, getLogger
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----------------------------------------------
# Configuração do Logfire
import logfire
logfire.configure()
basicConfig(handlers=[logfire.LogfireLoggingHandler()])
logger = getLogger(__name__)
logger.setLevel(logging.INFO)
logfire.instrument_requests()
logfire.instrument_sqlalchemy()

# ----------------------------------------------
# Configuração do logging
basicConfig(level=logging.INFO)

# Importar a base e livros do banco.py
from banco import Base, Livro

# Carrega as variáveis de ambiente
load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def criar_tabela():
    Base.metadata.create_all(engine)
    logger.info("Tabela criada|verificada com sucesso")
    """ inspector = inspect(engine)
    if '"LIVROS_ESTOQUE"' in inspector.get_table_names():
        with engine.connect() as conn:
            conn.execute(text('DROP TABLE IF EXISTS "LIVROS_ESTOQUE" CASCADE'))
            conn.commit()
            """
    

base_url = "https://books.toscrape.com/catalogue/"
start_url = "https://books.toscrape.com/catalogue/page-1.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0"
}

estrelas_dict = {
    'One': '1 estrela',
    'Two': '2 estrelas',
    'Three': '3 estrelas',
    'Four': '4 estrelas',
    'Five': '5 estrelas'
}

def buscar_categoria(link):
    try:
        site = requests.get(link, headers=headers)
        soup = BeautifulSoup(site.content, "html.parser")
        categoria = soup.find('ul', {'class': 'breadcrumb'}).find_all('a')[2].text.strip()
        return categoria
    except Exception:
        return "Categoria desconhecida"

def buscar_livros(url):
    """Busca os livros na página especificada"""
    try:
        site = requests.get(url, headers=headers)
        soup = BeautifulSoup(site.content, "html.parser")
        livros = []
        for livro in soup.find_all('article', {'class': 'product_pod'}):
            titulo = livro.find('h3').find('a')['title']
            estrelas = livro.find('p', {'class': 'star-rating'})
            classificacao = estrelas_dict.get(estrelas['class'][1], "Sem avaliação") if estrelas else "Sem avaliação"
            preco = livro.find('p', {'class': 'price_color'}).text.strip()
            estoque = livro.find('p', {'class': 'instock availability'}).text.strip()
            link = base_url + livro.find('h3').find('a')['href']
            categoria = buscar_categoria(link)
            livros.append((titulo, classificacao, categoria, preco, estoque))
        logger.info(f"{len(livros)} livros extraídos de {url}")
        return livros
    except Exception as e:
        logger.error(f"Erro ao buscar livros em {url}: {e}")
        return []

def transformar_dados_livros(dados):
    resultados = []
    for dado in dados:
        titulo = dado[0]
        classificacao = dado[1]
        categoria = dado[2]
        preco = float(dado[3].replace('£', '').replace(',', '.'))
        estoque = dado[4]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dados_transformados = {
            "titulo": titulo,
            "classificacao": classificacao,
            "categoria": categoria,
            "preco": preco,
            "estoque": estoque,
            "timestamp": timestamp
        }
        resultados.append(dados_transformados)
    return resultados

def salvar_dados_postgres(dados):
    try:
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        cur = conn.cursor()
        for dado in dados:
            titulo = dado['titulo']
            classificacao = dado['classificacao']
            categoria = dado['categoria']
            preco = dado['preco']
            estoque = dado['estoque']
            timestamp = dado['timestamp']
            query = """
                INSERT INTO "LIVROS_ESTOQUE" (titulo, classificacao, categoria, preco, estoque, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (titulo, preco) DO NOTHING;
            """
            cur.execute(query, (titulo, classificacao, categoria, preco, estoque, timestamp))
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"{len(dados)} registros salvos com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao salvar dados: {e}")

def buscar_todas_paginas():
    urls = []
    url = start_url
    while url:
        site = requests.get(url, headers=headers)
        soup = BeautifulSoup(site.content, "html.parser")
        urls.append(url)
        next_page = soup.find('li', {'class': 'next'})
        if next_page:
            url = base_url + next_page.find('a')['href']
        else:
            break
    logger.info(f"{len(urls)} páginas encontradas.")
    return urls

def processar_pagina(url):
    livros = buscar_livros(url)
    if livros:
        dados_transformados = transformar_dados_livros(livros)
        salvar_dados_postgres(dados_transformados)

def main():
    criar_tabela()
    urls = buscar_todas_paginas()

    start_time = time.time()

    # Paraleliza a leitura e gravação usando ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(processar_pagina, url) for url in urls]

        for future in as_completed(futures):
            try:
                future.result()
            
            except Exception as e:
                logger.error(f"Erro em um dos workers: {e}")

    end_time = time.time()
    logger.info(f"Processamento finalizado em {round(end_time - start_time, 2)} segundos")

if __name__ == "__main__":
    main()
