import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv

# --- Configuração Inicial ---
# Carrega o .env da raiz do projeto (lugar usual). Use .env.example como modelo.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Token de autenticação. A API do GitHub exige para evitar limite baixo de uso.
TOKEN = os.getenv("GITHUB_TOKEN")

# Endereço da API GraphQL do GitHub. Toda consulta é um POST com o texto da query.
URL = "https://api.github.com/graphql"

# Validação Fail-Fast: Impede o script de rodar (e gastar requisições) se não houver token.
if not TOKEN:
    raise ValueError("GITHUB_TOKEN não encontrado. Verifique seu arquivo .env.")

# --- Query GraphQL (Trazendo 100 de uma vez) ---
# GraphQL é uma linguagem em que VOCÊ escreve o que quer (quais campos) e o
# servidor devolve só isso. O formato da pergunta define o formato da resposta.
#
# Mapeamento para o Laboratório:
# - search: filtro para mais de 10k estrelas, ordenado do maior para o menor.
# - first: 100 (traz 100 itens de uma vez, máximo permitido sem paginação).
# - Os campos internos representam as métricas das questões de pesquisa (RQ01 a RQ06).
QUERY = """
{
  search(query: "stars:>10000 sort:stars-desc", type: REPOSITORY, first: 100) {
    nodes {
      ... on Repository {
        nameWithOwner
        createdAt                                            # RQ01: idade do repo (data de criação)
        stargazerCount                                       # quantidade de estrelas (para conferência)
        pullRequests(states: MERGED) { totalCount }          # RQ02: PRs aceitas (merged)
        releases { totalCount }                              # RQ03: total de releases
        updatedAt                                            # RQ04: data da última atualização
        primaryLanguage { name }                             # RQ05: linguagem principal
        issues { totalCount }                                # RQ06: total de issues
        closedIssues: issues(states: CLOSED) { totalCount }  # RQ06: issues fechadas
      }
    }
  }
}
"""

def fetch_sprint_1(max_retries: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    Executa a coleta da Sprint 1 em uma única chamada.
    Utiliza requests.Session para otimizar a conexão e um sistema de backoff exponencial
    para lidar com os erros 502 do GitHub.
    """
    print("Iniciando coleta da Sprint 1 (100 repositórios em uma requisição)...")
    
    # O Session reaproveita a mesma conexão TCP (Keep-Alive) por debaixo dos panos.
    # Isso reduz a latência e ajuda a evitar o erro 502 (Bad Gateway).
    with requests.Session() as session:
        session.headers.update({"Authorization": f"Bearer {TOKEN}"})
        
        for attempt in range(max_retries):
            try:
                # POST: envia a query como body JSON.
                # Timeout aumentado para 45s: dá mais tempo para o GitHub calcular
                # as agregações de PRs, Issues e Releases dos 100 repositórios.
                response = session.post(URL, json={"query": QUERY}, timeout=45)
                
                # Tratamento de erro 502/503/504: falha temporária por sobrecarga no GitHub.
                if response.status_code in (502, 503, 504):
                    wait_time = 2 ** attempt # Espera progressiva: 1s, 2s, 4s, 8s, 16s...
                    print(f"Erro {response.status_code} no servidor. Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                # Levanta exceção silenciosamente se for outro erro HTTP (ex: 401 Unauthorized por token errado)
                response.raise_for_status()
                
                data = response.json()
                
                # A API GraphQL retorna status 200 OK mesmo quando há erros de sintaxe na query.
                # Precisamos checar ativamente se a chave "errors" veio no JSON.
                if "errors" in data:
                    print(f"Erro na sintaxe da Query: {data['errors'][0]['message']}")
                    return None
                    
                repos = data.get("data", {}).get("search", {}).get("nodes", [])
                print(f"\nSucesso! Foram retornados {len(repos)} repositórios.")
                return repos

            except requests.RequestException as e:
                # Captura falhas de internet ou timeout local
                print(f"Erro de rede ou conexão: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

    print("\nFalha: O número máximo de tentativas foi atingido. O GitHub não conseguiu processar a carga.")
    return None

if __name__ == "__main__":
    repositorios = fetch_sprint_1()
    
    if repositorios:
        print("\nAmostra dos resultados:")
        for repo in repositorios[:5]:
            print(f"- {repo['nameWithOwner']} ({repo['stargazerCount']} estrelas)")