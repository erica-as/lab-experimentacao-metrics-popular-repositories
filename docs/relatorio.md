# Relatório – Laboratório 01: Características de Repositórios Populares

**Disciplina:** Laboratório de Experimentação de Software  
**Data:** março de 2026  

---

## 1. Introdução

Este relatório apresenta a análise dos **1.000 repositórios com maior número de estrelas no GitHub**, coletados via API GraphQL. O objetivo é investigar características comuns a sistemas populares — como maturidade, frequência de contribuições, lançamento de releases, atualização, linguagem de programação e gestão de issues — e relacioná-las com o sucesso medido pela popularidade (estrelas).

As seções a seguir apresentam hipóteses informais para cada questão de pesquisa (RQ), que serão validadas ou refutadas com base nos dados coletados.

---

## 2. Metodologia

Os dados foram coletados por meio de um script Python que consome a **API GraphQL do GitHub** (`https://api.github.com/graphql`). A consulta utiliza paginação via `endCursor` para recuperar os 1.000 repositórios com mais estrelas.

Para cada repositório foram coletadas as seguintes informações:

| Campo | Descrição |
|---|---|
| `nameWithOwner` | Nome do repositório (owner/repo) |
| `createdAt` | Data de criação |
| `stargazerCount` | Número de estrelas |
| `pullRequestsMerged` | Total de pull requests aceitas (estado `MERGED`) |
| `releasesTotal` | Total de releases publicadas |
| `updatedAt` | Data da última atualização |
| `primaryLanguage` | Linguagem de programação principal |
| `issuesTotal` | Total de issues (abertas + fechadas) |
| `issuesClosed` | Total de issues fechadas |

Os dados foram persistidos em `data/repos.csv`. A análise será realizada com base em **valores medianos** para métricas numéricas e **contagem por categoria** para métricas categóricas (como linguagem de programação).

---

## 3. Questões de Pesquisa e Hipóteses Informais

### RQ01 — Sistemas populares são maduros/antigos?

**Métrica:** Idade do repositório, calculada em anos a partir de `createdAt` até a data de coleta.

**Hipótese:** Espera-se que a maioria dos repositórios populares seja relativamente antiga (mediana acima de 5 anos). Projetos consolidados têm mais tempo para acumular estrelas, construir comunidade e se tornar referências em suas áreas. Repositórios muito novos dificilmente atingem o topo sem um evento viral específico, que geralmente é raro.

---

### RQ02 — Sistemas populares recebem muita contribuição externa?

**Métrica:** Total de pull requests aceitas (`MERGED`).

**Hipótese:** Espera-se que repositórios populares possuam um número elevado de pull requests mescladas, indicando ampla contribuição da comunidade. Projetos com muitas estrelas tendem a atrair mais desenvolvedores dispostos a contribuir. No entanto, repositórios do tipo "lista" ou "tutorial" podem ter baixo volume de PRs mesmo sendo muito populares.

---

### RQ03 — Sistemas populares lançam _releases_ com frequência?

**Métrica:** Total de releases publicadas.

**Hipótese:** Espera-se que a maioria dos repositórios populares que são projetos de software ativo tenha um número considerável de releases. Contudo, repositórios do tipo "awesome lists", documentação ou coleções de recursos frequentemente não utilizam o sistema de releases do GitHub, o que pode reduzir a mediana geral. Portanto, a hipótese é de que a mediana seja moderada, com alta variância.

---

### RQ04 — Sistemas populares são atualizados com frequência?

**Métrica:** Tempo desde a última atualização, calculado em dias a partir de `updatedAt` até a data de coleta.

**Hipótese:** Espera-se que os repositórios populares sejam atualizados com frequência, apresentando mediana de tempo desde a última atualização muito baixa (poucos dias). A popularidade tende a atrair contribuidores ativos que mantêm o projeto vivo e em evolução contínua.

---

### RQ05 — Sistemas populares são escritos nas linguagens mais populares?

**Métrica:** Linguagem primária (`primaryLanguage`) de cada repositório.

**Hipótese:** Espera-se que linguagens amplamente adotadas no mercado — como **JavaScript**, **Python**, **TypeScript** e **Java** — dominem entre os repositórios mais populares. Isso se deve tanto à maior base de usuários dessas linguagens quanto ao fato de que projetos nessas tecnologias tendem a resolver problemas mais comuns e acessíveis a um público maior.

---

### RQ06 — Sistemas populares possuem um alto percentual de _issues_ fechadas?

**Métrica:** Razão entre issues fechadas (`issuesClosed`) e total de issues (`issuesTotal`).

**Hipótese:** Espera-se que repositórios populares apresentem uma taxa relativamente alta de issues fechadas, indicando boa manutenção e atenção às demandas da comunidade. Projetos bem gerenciados tendem a atrair mais contribuidores, o que facilita a resolução de problemas. A mediana da razão deve ficar acima de 70%.

---

### Bônus — RQ07: Linguagens mais populares influenciam contribuição, releases e atualizações?

**Métrica:** Análise das métricas das RQs 02, 03 e 04 segmentadas por linguagem de programação.

**Hipótese:** Espera-se que repositórios escritos em linguagens com maior base de usuários (como JavaScript e Python) apresentem maior volume de pull requests e atualizações mais frequentes. Em relação a releases, linguagens associadas a bibliotecas e frameworks (como JavaScript/TypeScript via npm) podem apresentar maior frequência de publicação, pois o versionamento via releases é uma prática comum nesse ecossistema.

---

## 4. Próximos Passos

Na próxima etapa (Lab01S03), serão realizadas:

- Análise estatística dos dados coletados (medianas, distribuições, outliers).
- Criação de visualizações gráficas para apoiar a discussão.
- Comparação dos resultados com as hipóteses levantadas neste documento.
- Elaboração da versão final do relatório com conclusões e discussão completa.
