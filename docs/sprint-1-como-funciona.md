# Sprint 1 (Lab01S01) – Como funciona e aderência

## O que a Sprint 1 pede (especificação)

- **Consulta GraphQL** para **100 repositórios**, com **todos os dados/métricas** necessários para responder às RQs.
- **Requisição automática**: um script seu que chama a API (não pode usar biblioteca de terceiros que faça a consulta ao GitHub por você).

## Como o script faz isso

1. **Configuração**
   - Lê o token do GitHub do arquivo `.env` na raiz do projeto (variável `GITHUB_TOKEN`).
   - Usa a URL da API GraphQL do GitHub e o cabeçalho de autenticação.

2. **Query GraphQL**
   - Você escreve um “texto” que descreve o que quer. O script envia esse texto no corpo de um **POST** para a API.
   - A query pede:
     - `search` com filtro `stars:>10000 sort:stars-desc` e `first: 100` → os 100 repositórios mais estrelados (acima de 10k estrelas).
     - Para cada repositório, os campos usados nas RQs (veja tabela abaixo).

3. **Requisição automática**
   - O script usa a biblioteca `requests` só para fazer o HTTP (POST com a query em JSON).
   - A **query em si** foi escrita no código; não há lib que “consulte o GitHub” por você → atende à restrição da especificação.

4. **Resposta**
   - A API devolve JSON. O script lê `data.search.nodes` (lista de 100 repos) e imprime um resumo (quantidade e os 5 primeiros).

## Aderência às RQs (métricas na query)

| RQ  | Métrica no relatório | Campo na query GraphQL |
|-----|----------------------|-------------------------|
| RQ01 | Idade do repositório | `createdAt` |
| RQ02 | Total de PRs aceitas | `pullRequests(states: MERGED) { totalCount }` |
| RQ03 | Total de releases | `releases { totalCount }` |
| RQ04 | Tempo até última atualização | `updatedAt` |
| RQ05 | Linguagem primária | `primaryLanguage { name }` |
| RQ06 | Razão issues fechadas / total | `issues { totalCount }` e `issues(states: CLOSED) { totalCount }` |

Todos os dados necessários para as RQs estão na query. A razão da RQ06 é calculada depois (fechadas ÷ total), a partir desses dois contadores.

## Erro 502 ao rodar

**O que é:** HTTP 502 Bad Gateway = falha temporária no servidor (no caso, do lado do GitHub), não no seu código nem no token.

**O que o script faz:** Tenta de novo até 3 vezes, com espera entre tentativas (1 s, 2 s). Se as 3 derem 502, ele apenas informa o erro.

**O que você pode fazer:**
- Esperar alguns minutos e rodar de novo (`python3 src/main.py`).
- Verificar se há incidentes: [GitHub Status](https://www.githubstatus.com/).
- Se persistir por muito tempo, tentar em outro horário ou rede (ex.: outro Wi‑Fi ou celular como hotspot).

Não é problema de autenticação (token errado costuma dar 401) nem de limite de taxa (403 com mensagem de rate limit).
