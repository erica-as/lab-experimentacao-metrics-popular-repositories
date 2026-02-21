import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
URL = "https://api.github.com/graphql"

headers = {"Authorization": f"Bearer {TOKEN}"}

query = """
{
  search(query: "stars:>10000 sort:stars-desc", type: REPOSITORY, first: 100) {
    nodes {
      ... on Repository {
        nameWithOwner
        createdAt # RQ 01
        stargazerCount
        pullRequests(states: MERGED) { totalCount } # RQ 02
        releases { totalCount } # RQ 03
        updatedAt # RQ 04
        primaryLanguage { name } # RQ 05
        issues { totalCount } # RQ 06
        closedIssues: issues(states: CLOSED) { totalCount } # RQ 06
      }
    }
  }
}
"""

def fetch_sprint_1():
    print(f"Iniciando coleta da Sprint 1 (100 repositórios)...")
    response = requests.post(URL, json={'query': query}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print("Erro na Query:", data['errors'][0]['message'])
        else:
            repos = data['data']['search']['nodes']
            print(f"Sucesso! Foram retornados {len(repos)} repositórios.")
            
            for repo in repos[:5]:
                print(f"- {repo['nameWithOwner']} ({repo['stargazerCount']} estrelas)")
    else:
        print(f"Erro no servidor: {response.status_code}")

if __name__ == "__main__":
    fetch_sprint_1()