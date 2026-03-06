import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv

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

# --- Query paginada (Sprint 2) ---
# Usa variável $cursor para paginação via endCursor.
# Inclui rateLimit para detectar e respeitar limites da API.
QUERY_PAGINATED = """
query($cursor: String) {
  search(query: "stars:>1000 sort:stars-desc", type: REPOSITORY, first: 10, after: $cursor) {
    pageInfo {
      endCursor
      hasNextPage
    }
    nodes {
      ... on Repository {
        nameWithOwner
        createdAt
        stargazerCount
        pullRequests(states: MERGED) { totalCount }
        releases { totalCount }
        updatedAt
        primaryLanguage { name }
        issues { totalCount }
        closedIssues: issues(states: CLOSED) { totalCount }
      }
    }
  }
  rateLimit {
    remaining
    resetAt
  }
}
"""


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
                        break 

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


def fetch_sprint_2(total: int = 1000, page_size: int = 10, max_retries: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    Faz requisições paginadas à API GraphQL do GitHub usando cursor/endCursor,
    acumulando resultados em lotes de `page_size` até atingir `total` repositórios.
    Trata rate limit (aguarda reset quando necessário) e erros 502/503/504 com
    backoff exponencial.
    """
    print(f"Iniciando coleta da Sprint 2 — paginação (lotes de {page_size}, meta: {total} repositórios)...")

    collected: List[Dict[str, Any]] = []
    cursor: Optional[str] = None

    with requests.Session() as session:
        session.headers.update({"Authorization": f"Bearer {TOKEN}"})

        while len(collected) < total:
            page_num = len(collected) // page_size + 1
            print(f"\n[Página {page_num}] Buscando até {page_size} repos (cursor: {cursor!r})...")

            payload = {"query": QUERY_PAGINATED, "variables": {"cursor": cursor}}

            for attempt in range(max_retries):
                try:
                    response = session.post(URL, json=payload, timeout=45)

                    if response.status_code in (502, 503, 504):
                        wait_time = 2 ** attempt
                        print(f"  Erro {response.status_code}. Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s...")
                        time.sleep(wait_time)
                        continue

                    response.raise_for_status()
                    data = response.json()

                    if "errors" in data:
                        print(f"  Erro na Query: {data['errors'][0]['message']}")
                        return None

                    search = data.get("data", {}).get("search", {})
                    nodes = search.get("nodes", [])
                    page_info = search.get("pageInfo", {})

                    rate_limit = data.get("data", {}).get("rateLimit", {})
                    remaining = rate_limit.get("remaining")
                    reset_at = rate_limit.get("resetAt")
                    if remaining is not None and remaining < 5 and reset_at:
                        reset_time = datetime.fromisoformat(reset_at.rstrip("Z")).replace(tzinfo=timezone.utc)
                        wait_seconds = (reset_time - datetime.now(timezone.utc)).total_seconds()
                        if wait_seconds > 0:
                            print(f"  Rate limit quase esgotado ({remaining} restantes). Aguardando {wait_seconds:.0f}s até reset...")
                            time.sleep(wait_seconds + 1)

                    slots_left = total - len(collected)
                    collected.extend(nodes[:slots_left])
                    print(f"  Recebidos: {len(nodes)} repos (total em memória: {len(collected)})")

                    if not page_info.get("hasNextPage", False):
                        print("  Sem mais páginas disponíveis.")
                        print(f"\nColeta finalizada: {len(collected)} repositórios coletados.")
                        return collected

                    cursor = page_info.get("endCursor")
                    break  

                except requests.RequestException as e:
                    print(f"  Erro de rede: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    print(f"  Falha definitiva nesta página após {max_retries} tentativas.")
                    print(f"\nColeta interrompida: {len(collected)} repositórios coletados.")
                    return collected

    print(f"\nColeta finalizada: {len(collected)} repositórios coletados.")
    return collected


def _nested_count(repo: Dict[str, Any], key: str) -> int:
    """Retorna totalCount de um campo aninhado, ou 0 se ausente."""
    return (repo.get(key) or {}).get("totalCount", 0)


def save_to_csv(repos: List[Dict[str, Any]], path: str = "data/repos.csv") -> None:
    """Salva os repositórios coletados em um arquivo CSV em `data/`."""
    output_path = Path(__file__).resolve().parent.parent / path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "nameWithOwner",
        "createdAt",
        "stargazerCount",
        "pullRequestsMerged",
        "releasesTotal",
        "updatedAt",
        "primaryLanguage",
        "issuesTotal",
        "issuesClosed",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for repo in repos:
            writer.writerow({
                "nameWithOwner": repo.get("nameWithOwner", ""),
                "createdAt": repo.get("createdAt", ""),
                "stargazerCount": repo.get("stargazerCount", 0),
                "pullRequestsMerged": _nested_count(repo, "pullRequests"),
                "releasesTotal": _nested_count(repo, "releases"),
                "updatedAt": repo.get("updatedAt", ""),
                "primaryLanguage": (repo.get("primaryLanguage") or {}).get("name", ""),
                "issuesTotal": _nested_count(repo, "issues"),
                "issuesClosed": _nested_count(repo, "closedIssues"),
            })
    print(f"Dados salvos em {output_path} ({len(repos)} repositórios).")


if __name__ == "__main__":
    repositorios = fetch_sprint_2()

    if repositorios:
        repositorios_ordenados = sorted(repositorios, key=lambda r: r['stargazerCount'], reverse=True)
        print("\nTop 10 (ordem decrescente de estrelas):")
        for repo in repositorios_ordenados[:10]:
            print(f"- {repo['nameWithOwner']} ({repo['stargazerCount']} estrelas)")
        save_to_csv(repositorios_ordenados)