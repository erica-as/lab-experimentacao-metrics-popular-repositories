# Glossário e conceitos – Laboratório 01

Introdução aos jargões e conceitos usados na especificação do laboratório (características de repositórios populares).

---

## 1. Contexto do laboratório

- **Open-source** — Software cujo código-fonte é público e pode ser usado, modificado e redistribuído (geralmente sob licença como MIT, GPL, Apache). O laboratório fala de “sistemas populares open-source” = projetos famosos nesse modelo.
- **GitHub** — Plataforma de hospedagem de repositórios Git. “Repositórios com maior número de estrelas” = projetos ranqueados pela métrica *stars* do GitHub.

---

## 2. Termos do GitHub (métricas e artefatos)

- **Estrelas (stars)** — Botão “Star” no GitHub: usuários marcam o repo como favorito. Serve como indicador de popularidade (não é “qualidade”, é “visibilidade/ interesse”).
- **Repositório (repo)** — Um projeto no GitHub: código, histórico, issues, PRs, releases etc. “1.000 repositórios” = 1.000 projetos.
- **Pull request (PR)** — Proposta de alteração no código: alguém sugere mudanças (branch) para serem incorporadas ao branch principal. **“Pull requests aceitas”** = PRs que foram **merged** (incorporadas). No lab, isso é usado como proxy de **contribuição externa**.
- **Release** — Versão publicada do projeto (ex.: v1.0.0), geralmente com tag e às vezes com binários/instaladores. “Total de releases” indica com que frequência o projeto “lança” versões.
- **Issue** — Registro de bug, melhoria ou discussão (aberta ou fechada). **Issues fechadas** = resolvidas ou encerradas. A **razão (issues fechadas / total de issues)** mede tendência a “fechar” o que foi aberto (gestão do backlog).
- **Linguagem primária (primary language)** — Linguagem que o GitHub detecta como predominante no repositório (por linhas de código). No lab, usada para RQ05 e RQ07.
- **Data de criação (createdAt)** — Quando o repositório foi criado no GitHub. **Idade do repositório** = tempo desde essa data até hoje (ou até a data da análise).
- **Última atualização (updatedAt)** — Data do último evento que “mexeu” no repo (commit, issue, PR, etc.). **“Tempo até a última atualização”** = quanto tempo faz desde a última atividade; usado para ver se o projeto está “ativo” ou parado.

---

## 3. Termos de pesquisa e metodologia

- **Questão de pesquisa (RQ — Research Question)** — Pergunta que o estudo quer responder com dados. O lab tem RQ01–RQ06 (+ RQ07 bônus); cada RQ tem uma **métrica** associada.
- **Métrica** — Grandeza que você mede para responder uma RQ (ex.: idade do repo, total de PRs merged, total de releases, razão de issues fechadas).
- **Hipótese informal** — Expectativa que você tem antes de ver os dados (ex.: “repos populares devem ser mais antigos”). No relatório, você compara essas hipóteses com os **resultados**.
- **Valor mediano (mediana)** — Valor do “meio” da amostra quando ordenada (metade abaixo, metade acima). A especificação pede **sumarização por medianas** (em vez de só média) para reduzir efeito de outliers.
- **Valores de categoria / contagem por categoria** — Dados nominais (ex.: linguagem: JavaScript, Python, …). “Contagem por categoria” = quantos repos em cada linguagem; usado em RQ05 e no bônus RQ07.
- **Metodologia** — No relatório, a parte em que você descreve **como** coletou e processou os dados (API, query, paginação, filtros, script) para responder às RQs.

---

## 4. Termos técnicos do processo (API e entrega)

- **API (Application Programming Interface)** — Interface que o GitHub expõe para programas acessarem dados (repos, stars, PRs, etc.) via HTTP. O lab usa a **API GraphQL** do GitHub.
- **GraphQL** — Linguagem de consulta em que o cliente define exatamente quais campos quer. Você monta uma **query** (texto) e envia por POST; a API devolve só esses campos. “Consulta GraphQL” = essa query + uma chamada à API.
- **Query** — No contexto do lab, o texto da sua consulta GraphQL (campos como `createdAt`, `stargazerCount`, `pullRequests`, `releases`, etc.).
- **Paginação** — A API devolve um número limitado de itens por vez (ex.: 100). Para obter 1.000 repositórios, você precisa fazer várias requisições usando cursor/“próxima página” = **paginação**.
- **Requisição automática** — Script (ex.: Python) que chama a API sem intervenção manual; não é “clicar no navegador”, é código que faz as chamadas.
- **.csv (Comma-Separated Values)** — Arquivo de texto com dados em linhas e colunas separadas por vírgula (ou outro delimitador). Formato simples para guardar os 1.000 repos e analisar no relatório.
- **Sprint (Lab01S01, S02, S03)** — No enunciado, são **etapas** do laboratório (S01: 100 repos + GraphQL + script; S02: 1.000 repos + CSV + hipóteses; S03: análise + relatório final), cada uma com pontuação definida.

---

## 5. Resumo rápido

| Jargão | Significado no lab |
|--------|---------------------|
| **Stars** | Popularidade do repo no GitHub |
| **PR merged** | Contribuição externa aceita |
| **Release** | Versão publicada do projeto |
| **Issue fechada / total** | Proporção do backlog “resolvido” |
| **Primary language** | Linguagem principal do repo |
| **RQ** | Pergunta de pesquisa (com métrica definida) |
| **Hipótese informal** | O que você espera antes de ver os dados |
| **Mediana** | Valor do meio; sumarização pedida no relatório |
| **GraphQL / query** | Forma de pedir só os campos necessários à API do GitHub |
| **Paginação** | Múltiplas requisições para atingir 1.000 repos |
| **.csv** | Formato de armazenamento dos dados coletados |
