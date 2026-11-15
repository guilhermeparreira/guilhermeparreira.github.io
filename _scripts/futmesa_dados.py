"""Build the JSON consumed by the Futmesa pages from the futmesa-brasileirao Parquet files.

The site never fixes data: it only selects columns and derives presentation fields
(edition label, partial-edition flag, debut state, display and short names, grouped categories).

Usage:
    python _scripts/futmesa_dados.py                      # downloads the Parquet files from GitHub
    python _scripts/futmesa_dados.py --origem ../futmesa-brasileirao/saida
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import date
from pathlib import Path

import polars as pl

REPO_RAW = "https://raw.githubusercontent.com/guilhermeparreira/futmesa-brasileirao/main/saida"
ARQUIVOS = ("classificacao.parquet", "campeonatos.parquet")
RAIZ = Path(__file__).resolve().parent.parent
CACHE = RAIZ / ".futmesa_cache"
SAIDA = RAIZ / "futmesa" / "dados" / "brasileiro.json"

# An edition is "partial" when the source lists clearly fewer people than took part.
FRACAO_MINIMA_DOS_INFORMADOS = 0.9
MINIMO_DE_LINHAS = 60

PARTICULAS = {"de", "da", "do", "das", "dos", "e"}

# Categories that existed in a single edition are shown together with the closest one.
CATEGORIA_AGRUPADA = {"Sub-20": "Sub-18", "Infantil": "Sub-15"}

# Years without championship, kept on the charts' time axis with blank statistics.
ANOS_SEM_CAMPEONATO = [
    {"ano": 2020, "rotulo": "2020 - Pandemia"},
    {"ano": 2021, "rotulo": "2021 - Pandemia"},
]


def baixar_parquets(destino: Path) -> Path:
    """Download the Parquet files published by futmesa-brasileirao."""
    destino.mkdir(parents=True, exist_ok=True)
    for nome in ARQUIVOS:
        urllib.request.urlretrieve(f"{REPO_RAW}/{nome}", destino / nome)
    return destino


def nome_de_exibicao(nome: str | None) -> str | None:
    """Turn 'JEFFERSON DO AMARAL GENTA' into 'Jefferson do Amaral Genta'."""
    if nome is None:
        return None
    palavras = nome.lower().split()
    return " ".join(
        p if (p in PARTICULAS and i > 0) else p[:1].upper() + p[1:]
        for i, p in enumerate(palavras)
    )


def nome_curto(nome: str, apelidos: list[str], impressos: list[str]) -> str:
    """Pick one short name: nickname, else the usual one-word printed name, else first + last name."""
    if apelidos:
        return apelidos[0]
    de_uma_palavra = [i for i in impressos if i and len(i.split()) == 1]
    if de_uma_palavra:
        return nome_de_exibicao(max(set(de_uma_palavra), key=de_uma_palavra.count))
    palavras = nome.split()
    return nome if len(palavras) <= 2 else f"{palavras[0]} {palavras[-1]}"


def montar_nomes(classificacao: pl.DataFrame) -> pl.DataFrame:
    """One display name and one short name per person (the most frequent standardized name)."""
    pessoas = (
        classificacao.filter(pl.col("id_botonista").is_not_null())
        .sort("ano")
        .group_by("id_botonista")
        .agg(
            pl.col("botonista_padronizado").mode().sort().last().alias("nome"),
            pl.col("apelido").drop_nulls().alias("apelidos"),
            pl.col("botonista").alias("impressos"),
        )
    )
    nomes = [nome_de_exibicao(p["nome"]) for p in pessoas.iter_rows(named=True)]
    curtos = [
        nome_curto(nome, p["apelidos"], p["impressos"])
        for nome, p in zip(nomes, pessoas.iter_rows(named=True))
    ]
    return pessoas.select("id_botonista").with_columns(
        nome=pl.Series(nomes), curto=pl.Series(curtos)
    )


def montar_edicoes(classificacao: pl.DataFrame, campeonatos: pl.DataFrame) -> list[dict]:
    linhas_por_ano = classificacao.group_by("ano").agg(pl.len().alias("linhas"))
    edicoes = (
        campeonatos.join(linhas_por_ano, on="ano", how="left")
        .with_columns(
            parcial=(
                pl.col("linhas")
                < FRACAO_MINIMA_DOS_INFORMADOS * pl.col("participantes_informados")
            ).fill_null(False)
            | (pl.col("linhas") < MINIMO_DE_LINHAS),
            rotulo=pl.format(
                "{} - {} ({})", "ano", "cidade_campeonato", "uf_campeonato"
            ),
        )
        .sort("ano")
    )
    return edicoes.select(
        "ano",
        "edicao",
        "rotulo",
        cidade="cidade_campeonato",
        uf="uf_campeonato",
        informados="participantes_informados",
        linhas="linhas",
        parcial="parcial",
    ).to_dicts()


def montar_linhas(classificacao: pl.DataFrame) -> dict[str, list]:
    uf_estreia = (
        classificacao.filter(pl.col("uf_botonista").is_not_null())
        .sort("ano")
        .group_by("id_botonista")
        .agg(pl.col("uf_botonista").first().alias("uf_estreia"))
    )
    linhas = (
        classificacao.filter(pl.col("id_botonista").is_not_null())
        .join(uf_estreia, on="id_botonista", how="left")
        .join(montar_nomes(classificacao), on="id_botonista", how="left")
        .with_columns(categoria=pl.col("categoria").replace(CATEGORIA_AGRUPADA))
        .sort("ano", "categoria", "divisao_nivel", "posicao")
        .select(
            "ano",
            cat="categoria",
            div="divisao",
            niv="divisao_nivel",
            pos="posicao",
            id="id_botonista",
            nome="nome",
            curto="curto",
            uf="uf_botonista",
            ufo="uf_estreia",
            wo="wo",
            j="jogos",
            v="vitorias",
            e="empates",
            d="derrotas",
            gp="gols_pro",
            gc="gols_contra",
            pts="pontos",
        )
    )
    return linhas.to_dict(as_series=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--origem", type=Path, help="pasta com os Parquet (padrão: baixa do GitHub)")
    args = parser.parse_args()

    origem = args.origem or baixar_parquets(CACHE)
    classificacao = pl.read_parquet(origem / "classificacao.parquet")
    campeonatos = pl.read_parquet(origem / "campeonatos.parquet")

    dados = {
        "gerado_em": date.today().isoformat(),
        "edicoes": montar_edicoes(classificacao, campeonatos),
        "sem_campeonato": ANOS_SEM_CAMPEONATO,
        "linhas": montar_linhas(classificacao),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{SAIDA.relative_to(RAIZ)}: {len(dados['edicoes'])} edições, {len(dados['linhas']['ano'])} linhas")


if __name__ == "__main__":
    main()
