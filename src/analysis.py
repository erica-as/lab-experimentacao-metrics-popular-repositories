from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


DATA_CSV = Path(__file__).resolve().parent.parent / "data" / "repos.csv"
FIG_DIR = Path(__file__).resolve().parent.parent / "docs" / "figures"


def load_data(path: Path = DATA_CSV) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["createdAt", "updatedAt"], keep_default_na=False)

    # Ensure numeric columns
    for c in ["stargazerCount", "pullRequestsMerged", "releasesTotal", "issuesTotal", "issuesClosed"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    # Normalize empty primaryLanguage
    if "primaryLanguage" in df.columns:
        df["primaryLanguage"] = df["primaryLanguage"].replace({"": "Unknown", None: "Unknown"})

    return df


def compute_metrics(df: pd.DataFrame) -> dict:
    now = pd.to_datetime(datetime.now(timezone.utc))
    metrics = {}

    df["createdAt"] = pd.to_datetime(df["createdAt"], utc=True, errors="coerce")
    df["updatedAt"] = pd.to_datetime(df["updatedAt"], utc=True, errors="coerce")

    df["age_years"] = (now - df["createdAt"]).dt.days / 365.25
    df["days_since_update"] = (now - df["updatedAt"]).dt.days

    df["issuesTotal"] = pd.to_numeric(df.get("issuesTotal", pd.Series(dtype=float)), errors="coerce").fillna(0)
    df["issuesClosed"] = pd.to_numeric(df.get("issuesClosed", pd.Series(dtype=float)), errors="coerce").fillna(0)
    df["issues_closed_ratio"] = np.where(df["issuesTotal"] > 0, df["issuesClosed"] / df["issuesTotal"], np.nan)

    metrics["n_repos"] = len(df)
    metrics["median_age_years"] = float(df["age_years"].median())
    metrics["median_pr_merged"] = float(df.get("pullRequestsMerged", pd.Series(dtype=float)).median())
    metrics["median_releases"] = float(df.get("releasesTotal", pd.Series(dtype=float)).median())
    metrics["median_days_since_update"] = float(df["days_since_update"].median())
    metrics["median_issues_closed_ratio"] = float(df["issues_closed_ratio"].median(skipna=True) * 100)
    metrics["top_languages"] = df["primaryLanguage"].value_counts().head(10).to_dict()

    # Attach processed df for plotting
    metrics["df"] = df
    return metrics


def plot_and_save(metrics: dict, out_dir: Path = FIG_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = metrics["df"]
    sns.set(style="whitegrid")

    # Age histogram
    plt.figure(figsize=(8, 4))
    sns.histplot(df["age_years"].dropna(), bins=30, kde=False)
    plt.xlabel("Idade (anos)")
    plt.title("Distribuição de idade dos repositórios")
    plt.tight_layout()
    plt.savefig(out_dir / "age_hist.png")
    plt.close()

    # Days since update
    plt.figure(figsize=(8, 4))
    sns.histplot(df["days_since_update"].dropna(), bins=30, kde=False)
    plt.xlabel("Dias desde última atualização")
    plt.title("Tempo desde última atualização")
    plt.tight_layout()
    plt.savefig(out_dir / "updated_days_hist.png")
    plt.close()

    # Top languages bar
    top_lang = pd.Series(metrics["top_languages"])
    plt.figure(figsize=(10, 5))
    sns.barplot(x=top_lang.values, y=top_lang.index, palette="muted")
    plt.xlabel("Contagem")
    plt.ylabel("Linguagem")
    plt.title("Top 10 linguagens primárias entre os repositórios")
    plt.tight_layout()
    plt.savefig(out_dir / "top_languages.png")
    plt.close()

    # Issues closed ratio
    plt.figure(figsize=(8, 4))
    sns.histplot(df["issues_closed_ratio"].dropna() * 100, bins=30, kde=False)
    plt.xlabel("Percentual de issues fechadas (%)")
    plt.title("Distribuição do percentual de issues fechadas")
    plt.tight_layout()
    plt.savefig(out_dir / "issues_closed_ratio_hist.png")
    plt.close()

    # Stars vs PRs scatter
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=df.get("pullRequestsMerged", 0), y=df.get("stargazerCount", 0))
    plt.xscale("symlog")
    plt.yscale("symlog")
    plt.xlabel("Pull Requests mescladas (log escala)")
    plt.ylabel("Estrelas (log escala)")
    plt.title("Relação entre estrelas e pull requests mescladas")
    plt.tight_layout()
    plt.savefig(out_dir / "stars_vs_prs.png")
    plt.close()

    # Language-level summary (top 10 languages by count)
    lang_grp = df.groupby("primaryLanguage")
    lang_summary = pd.DataFrame({
        "count": lang_grp.size(),
        "median_prs_merged": lang_grp["pullRequestsMerged"].median(),
        "median_releases": lang_grp["releasesTotal"].median(),
        "median_days_since_update": lang_grp["days_since_update"].median(),
        "median_stars": lang_grp["stargazerCount"].median(),
    })

    lang_summary = lang_summary.sort_values("count", ascending=False)
    lang_summary.to_csv(out_dir / "language_summary.csv")

    top_langs = lang_summary.head(10)

    # Plot median PRs by language
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_langs["median_prs_merged"], y=top_langs.index, palette="vlag")
    plt.xlabel("Mediana de PRs mescladas")
    plt.ylabel("Linguagem")
    plt.title("Mediana de PRs mescladas por linguagem (top 10)")
    plt.tight_layout()
    plt.savefig(out_dir / "median_prs_by_language.png")
    plt.close()

    # Plot median releases by language
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_langs["median_releases"], y=top_langs.index, palette="crest")
    plt.xlabel("Mediana de releases")
    plt.ylabel("Linguagem")
    plt.title("Mediana de releases por linguagem (top 10)")
    plt.tight_layout()
    plt.savefig(out_dir / "median_releases_by_language.png")
    plt.close()

    # Plot median days since update by language
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_langs["median_days_since_update"], y=top_langs.index, palette="mako")
    plt.xlabel("Mediana de dias desde atualização")
    plt.ylabel("Linguagem")
    plt.title("Mediana de tempo de atualização por linguagem (top 10)")
    plt.tight_layout()
    plt.savefig(out_dir / "median_update_days_by_language.png")
    plt.close()


def print_summary(metrics: dict) -> None:
    print(f"Repositórios analisados: {metrics['n_repos']}")
    print(f"Mediana de idade (anos): {metrics['median_age_years']:.2f}")
    print(f"Mediana de PRs mescladas: {metrics['median_pr_merged']:.0f}")
    print(f"Mediana de releases: {metrics['median_releases']:.0f}")
    print(f"Mediana de dias desde atualização: {metrics['median_days_since_update']:.0f}")
    print(f"Mediana do percentual de issues fechadas: {metrics['median_issues_closed_ratio']:.1f}%")


def main():
    df = load_data()
    metrics = compute_metrics(df)
    print_summary(metrics)
    plot_and_save(metrics)
    print(f"Figuras salvas em: {FIG_DIR}")


if __name__ == "__main__":
    main()
