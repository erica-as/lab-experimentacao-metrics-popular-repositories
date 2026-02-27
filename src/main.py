import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv

# --- Configuração Inicial ---
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

TOKEN = os.getenv("GITHUB_TOKEN")

URL = "https://api.github.com/graphql"

if not TOKEN:
    raise ValueError("GITHUB_TOKEN não encontrado. Verifique seu arquivo .env.")

# --- Query ---
# Uma única query GraphQL parametrizada por intervalo de estrelas.
# Cada requisição busca 10 repositórios dentro de um range específico
# (sem cursor/paginação). 10 requisições × 10 repos = 100 no total.
QUERY = """
{{
  search(query: "stars:{star_filter} sort:stars-desc", type: REPOSITORY, first: 10) {{
    nodes {{
      ... on Repository {{
        nameWithOwner
        createdAt
        stargazerCount
        pullRequests(states: MERGED) {{ totalCount }}
        releases {{ totalCount }}
        updatedAt
        primaryLanguage {{ name }}
        issues {{ totalCount }}
        closedIssues: issues(states: CLOSED) {{ totalCount }}
      }}
    }}
  }}
}}
"""

# 10 intervalos não sobrepostos cobrindo repositórios com mais de 10k estrelas.
# Cada intervalo alimenta uma requisição independente.
# Intervalos ordenados do maior para o menor.
# O primeiro range usa >=100000 para garantir >=10 resultados no topo
# (repos acima de 200k são poucos e retornariam menos de 10).
STAR_RANGES = [
    ">=100000",
    "70000..99999",
    "50000..69999",
    "40000..49999",
    "30000..39999",
    "25000..29999",
    "20000..24999",
    "15000..19999",
    "12000..14999",
    "10000..11999",
]


def fetch_sprint_1(max_retries: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    Faz 10 requisições sequenciais e independentes à API GraphQL do GitHub,
    cada uma filtrando um intervalo de estrelas diferente (sem usar paginação).
    Os resultados são acumulados em memória. Cada requisição tem retry próprio
    com backoff exponencial para lidar com erros 502/503/504.
    """
    print(f"Iniciando coleta da Sprint 1 — {len(STAR_RANGES)} requisições sequenciais, 10 repos cada...")

    collected: List[Dict[str, Any]] = []

    with requests.Session() as session:
        session.headers.update({"Authorization": f"Bearer {TOKEN}"})

        for i, star_filter in enumerate(STAR_RANGES, start=1):
            query = QUERY.format(star_filter=star_filter)
            print(f"\n[{i}/{len(STAR_RANGES)}] Buscando repos com stars:{star_filter}...")

            for attempt in range(max_retries):
                try:
                    response = session.post(URL, json={"query": query}, timeout=45)

                    if response.status_code in (502, 503, 504):
                        wait_time = 2 ** attempt
                        print(f"  Erro {response.status_code}. Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s...")
                        time.sleep(wait_time)
                        continue

                    response.raise_for_status()
                    data = response.json()

                    if "errors" in data:
                        print(f"  Erro na Query: {data['errors'][0]['message']}")
                        break  # erro de query não adianta repetir

                    nodes = data.get("data", {}).get("search", {}).get("nodes", [])
                    collected.extend(nodes)
                    print(f"  Recebidos: {len(nodes)} repos (total em memória: {len(collected)})")
                    break

                except requests.RequestException as e:
                    print(f"  Erro de rede: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    print(f"  Falha definitiva neste intervalo após {max_retries} tentativas.")

    print(f"\nColeta finalizada: {len(collected)} repositórios coletados.")
    return collected


if __name__ == "__main__":
    repositorios = fetch_sprint_1()

    if repositorios:
        repositorios_ordenados = sorted(repositorios, key=lambda r: r['stargazerCount'], reverse=True)
        print("\nResultados (ordem decrescente de estrelas):")
        for repo in repositorios_ordenados:
            print(f"- {repo['nameWithOwner']} ({repo['stargazerCount']} estrelas)")