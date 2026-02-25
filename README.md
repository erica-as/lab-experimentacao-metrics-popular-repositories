# Laboratório 01 – Características de repositórios populares

Este repositório contém a elaboração do **Laboratório 01 – Características de repositórios populares**, da disciplina de **Laboratório de Experimentação de Software** (Engenharia de Software).

O objetivo é **coletar e analisar dados dos 1.000 repositórios com maior número de estrelas no GitHub**, a partir da API GraphQL, para responder às questões de pesquisa definidas na especificação.

> A [especificação oficial do laboratório](docs/especificacao.pdf) está em `docs/especificacao.pdf`.
>
> Para uma explicação dos principais termos e jargões, consulte o [glossário](wiki/Glossário.md) na Wiki. Mais documentação (como executar, Sprint 1) está em [wiki/](wiki/Home.md).

## Questões de pesquisa (RQs) e métricas

Para cada repositório analisado, devem ser coletadas as seguintes métricas, usadas para responder às RQs abaixo:

- **RQ01. Sistemas populares são maduros/antigos?**
  - **Métrica**: idade do repositório (calculada a partir da data de criação).

- **RQ02. Sistemas populares recebem muita contribuição externa?**
  - **Métrica**: total de _pull requests_ aceitas (estado `MERGED`).

- **RQ03. Sistemas populares lançam _releases_ com frequência?**
  - **Métrica**: total de _releases_.

- **RQ04. Sistemas populares são atualizados com frequência?**
  - **Métrica**: tempo até a última atualização (calculado a partir da data do último `updatedAt`).

- **RQ05. Sistemas populares são escritos nas linguagens mais populares?**
  - **Métrica**: linguagem primária (`primaryLanguage`) de cada repositório.

- **RQ06. Sistemas populares possuem um alto percentual de _issues_ fechadas?**
  - **Métrica**: razão entre o número de _issues_ fechadas (`CLOSED`) e o total de _issues_.

- **Bônus – RQ07. Sistemas escritos em linguagens mais populares recebem mais contribuição externa, lançam mais releases e são atualizados com mais frequência?**
  - **Métrica**: análise das métricas das RQs 02, 03 e 04 segmentadas por linguagem de programação.

## Relatório final

O relatório final deve:

- **(i)** apresentar uma **introdução simples com hipóteses informais** para cada RQ;
- **(ii)** descrever a **metodologia** utilizada para responder às questões de pesquisa;
- **(iii)** apresentar os **resultados obtidos** para cada RQ (valores agregados, como medianas, e contagens por categoria quando fizer sentido);
- **(iv)** discutir e **comparar os resultados com as hipóteses** levantadas inicialmente.

Orientações importantes:

- Para cada RQ, sumarizar os dados usando **valores medianos** (quando numéricos).
- Para valores categóricos (por exemplo, linguagem de programação), fazer **contagem por categoria** para facilitar a análise.

## Processo de desenvolvimento e pontuação

De acordo com a especificação (`docs/especificacao.pdf`), o laboratório é dividido em etapas, com a seguinte pontuação:

- **Lab01S01 – Consulta GraphQL para 100 repositórios + requisição automática (3 pontos)**
  - Escrever a **query GraphQL** contendo todas as métricas necessárias para as RQs.
  - Implementar um **script próprio** que consome a API GraphQL do GitHub e traz, no mínimo, **100 repositórios**.

- **Lab01S02 – Paginação, 1.000 repositórios + CSV + primeira versão do relatório (3 pontos)**
  - Implementar **paginação** na consulta para obter **1.000 repositórios**.
  - Persistir os dados em um arquivo, preferencialmente em formato **`.csv`** (pasta `data/`).
  - Produzir a **primeira versão do relatório**, com a definição das **hipóteses informais** para as RQs.

- **Lab01S03 – Análise, visualização de dados e relatório final (9 pontos)**
  - Realizar a **análise dos dados** coletados (medianas, distribuições, etc.).
  - (Opcional, mas desejável) Criar **visualizações** que apoiem a discussão dos resultados.
  - Finalizar o **relatório completo**, com resultados e discussão para todas as RQs.

- **Bônus – RQ07 por linguagem (+1 ponto)**
  - Dividir os resultados das **RQs 02, 03 e 04 por linguagem** de programação.
  - Investigar se sistemas escritos em linguagens mais populares apresentam mais contribuição externa, mais _releases_ e atualizações mais frequentes.

- **Valor total**: **15 pontos**, com **desconto de 1,0 ponto por dia de atraso**.

## Restrições importantes

- **Não é permitido o uso de bibliotecas de terceiros que realizem consultas à API do GitHub.**
  - A query GraphQL deve ser escrita pelo próprio aluno/grupo.
  - O consumo da API deve ser feito a partir de **um script próprio** (neste repositório).

## Como executar o código deste repositório

### Pré-requisitos

- Python 3.9+ instalado.
- Conta no GitHub com um **Personal Access Token** com permissão para acessar a API GraphQL.

### Passo a passo

**1. Ambiente virtual e dependências** (na raiz do projeto):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

No Windows, use `.venv\Scripts\pip` no lugar de `.venv/bin/pip`.

**2. Token do GitHub:** copie `.env.example` para `.env` na raiz do projeto e preencha:

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

**3. Rodar o script** (Sprint 1):

- Com o venv ativado: `python src/main.py`
- Sem ativar: `.venv/bin/python src/main.py` (Linux/macOS) ou `.venv\Scripts\python src/main.py` (Windows)

O script inicia a coleta da Sprint 1 (100 repositórios) e imprime um resumo no console. As próximas sprints estendem o código com paginação até 1.000 repos, export para CSV em `data/` e relatório final.

### Como funciona o ambiente virtual

Nada é instalado sozinho: você roda os comandos acima no terminal.

- **`python3 -m venv .venv`** — Cria a pasta `.venv` com uma cópia isolada do Python e do `pip`. O Python do sistema (ou do Homebrew) não é alterado.

- **`.venv/bin/pip install -r requirements.txt`** — Instala `requests` e `python-dotenv` apenas dentro de `.venv`. As dependências ficam no projeto, não no sistema.

- **`.env` (na raiz)** — O script lê o `.env` da raiz do projeto e carrega a variável `GITHUB_TOKEN` para autenticar na API do GitHub.

- **`.venv/bin/python src/main.py`** — Usa o Python do venv (que já tem as libs). O script carrega o `.env`, monta a query GraphQL e envia o POST para a API.

**Resumo:** use sempre os binários dentro de `.venv` (`.venv/bin/python` e `.venv/bin/pip`). Assim as dependências ficam só neste projeto.
