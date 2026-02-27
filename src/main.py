import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv

# Configuração  
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

TOKEN = os.getenv("GITHUB_TOKEN")

URL = "https://api.github.com/graphql"

if not TOKEN:
    raise ValueError("GITHUB_TOKEN não encontrado. Verifique seu arquivo .env.")

def fetch_sprint_1(max_retries: int = 5, total: int = 20, batch_size: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    Executa a coleta da Sprint 1 em batches menores (paginados) e armazena resultados
    em memória à medida que cada batch é bem-sucedido. Cada batch tem retries
    independentes para lidar com 502/503/504 sem perder os dados já coletados.

    Parâmetros:
    - max_retries: número máximo de tentativas por batch
    - total: número total de repositórios desejados
    - batch_size: quantos repositórios pedir por requisição
    """
    if batch_size <= 0 or total <= 0:
        raise ValueError("'total' e 'batch_size' devem ser inteiros positivos")

    print(f"Iniciando coleta da Sprint 1 em batches ({batch_size} por requisição) até {total} repositórios.")

    # Query parametrizada para paginação (cursor-based)
    QUERY = """
    query($first: Int!, $after: String) {
      search(query: "stars:>10000 sort:stars-desc", type: REPOSITORY, first: $first, after: $after) {
        pageInfo { endCursor hasNextPage }
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
    }
    """

    collected: List[Dict[str, Any]] = []
    failed_batches: List[Dict[str, Any]] = []  # guarda info de batches que falharam

    with requests.Session() as session:
        session.headers.update({"Authorization": f"Bearer {TOKEN}"})

        cursor = None
        while len(collected) < total:
            need = min(batch_size, total - len(collected))

            # tenta o batch com retries locais
            success = False
            for attempt in range(max_retries):
                try:
                    payload = {"query": QUERY, "variables": {"first": need, "after": cursor}}
                    response = session.post(URL, json=payload, timeout=45)

                    if response.status_code in (502, 503, 504):
                        wait_time = 2 ** attempt
                        print(f"Erro {response.status_code} no servidor. Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s...")
                        time.sleep(wait_time)
                        continue

                    response.raise_for_status()
                    data = response.json()

                    if "errors" in data:
                        print(f"Erro na Query: {data['errors'][0]['message']}")
                        # Não faz sentido tentar novamente se a query está inválida
                        return None

                    search = data.get("data", {}).get("search", {})
                    nodes = search.get("nodes", [])
                    page_info = search.get("pageInfo", {})

                    collected.extend(nodes)
                    cursor = page_info.get("endCursor")
                    has_next = page_info.get("hasNextPage", False)

                    print(f"Batch recebido: {len(nodes)} itens (total coletado: {len(collected)}/{total})")

                    success = True
                    # se não há próxima página, interrompe o laço externo
                    if not has_next:
                        print("Sem mais páginas disponíveis na pesquisa.")
                        break
                    # avança para próximo batch
                    break

                except requests.RequestException as e:
                    print(f"Erro de rede/timeout no batch: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    # falhou definitivamente este batch
                    print("Falha definitiva neste batch após múltiplas tentativas. Registrando para possível retry posterior.")
                    failed_batches.append({"cursor": cursor, "size": need})

            if not success and not cursor:
                # se falhou no primeiro batch e não há cursor para avançar, aborta
                print("Não foi possível completar o primeiro batch. Abortando.")
                break

            # segurança: se não houver cursor (ex.: fim), interrompe
            if cursor is None:
                break

        # Tenta reprocessar batches que falharam (uma rodada simples)
        if failed_batches:
            print(f"Tentando reprocessar {len(failed_batches)} batch(es) que falharam...")
            remaining_failures: List[Dict[str, Any]] = []
            for fb in failed_batches:
                c = fb["cursor"]
                need = fb["size"]
                retry_success = False
                for attempt in range(max_retries):
                    try:
                        payload = {"query": QUERY, "variables": {"first": need, "after": c}}
                        response = session.post(URL, json=payload, timeout=45)
                        if response.status_code in (502, 503, 504):
                            time.sleep(2 ** attempt)
                            continue
                        response.raise_for_status()
                        data = response.json()
                        if "errors" in data:
                            print(f"Erro na Query ao reprocessar: {data['errors'][0]['message']}")
                            break
                        nodes = data.get("data", {}).get("search", {}).get("nodes", [])
                        collected.extend(nodes)
                        retry_success = True
                        print(f"Reprocessado com sucesso batch com cursor {c} ({len(nodes)} itens)")
                        break
                    except requests.RequestException as e:
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)
                            continue
                        print(f"Reprocessamento falhou para cursor {c}: {e}")
                if not retry_success:
                    remaining_failures.append(fb)

            if remaining_failures:
                print(f"Ainda restaram {len(remaining_failures)} batch(es) falhados. Prosseguindo com os resultados coletados.")

    # garante que não retornamos mais que o solicitado
    result = collected[:total]
    return result

if __name__ == "__main__":
    # pedir 100 repositórios no total, em batches de 5
    repositorios = fetch_sprint_1(total=100, batch_size=5)
    
    if repositorios:
        print("\nAmostra dos resultados:")
        for repo in repositorios[:100]:
            print(f"- {repo['nameWithOwner']} ({repo['stargazerCount']} estrelas)")