#!/usr/bin/env python3
"""Gera os gráficos de desempenho do Trabalho 4 (Link Extractor) a partir dos CSVs em results/.

Compara os 4 cenários:
  - python_cache
  - python_nocache
  - ruby_cache
  - ruby_nocache

Métricas geradas:
  1. tempo_medio.png: Comparativo de Tempo Médio de Resposta (ms)
  2. mediana_p50.png: Comparativo de Mediana de Tempo de Resposta (ms)
  3. percentil_95.png: Comparativo de p95 (ms)
  4. req_por_segundo.png: Comparativo de Vazão / Throughput (RPS)
  5. curva_percentis.png: Distribuição de percentis para cada carga
  6. tabela_resumo.md: Tabela consolidada com todas as métricas

Uso:
  .venv/Scripts/python scripts/plot.py [--results results] [--out graficos]
"""
import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
PADRAO_ARQ = re.compile(r"([a-z_]+)_u(\d+)_stats\.csv")

ROTULOS = {
    "python_cache": "Python c/ Cache",
    "python_nocache": "Python s/ Cache",
    "ruby_cache": "Ruby c/ Cache",
    "ruby_nocache": "Ruby s/ Cache",
}

CORES = {
    "python_cache": "#2b6cb0",
    "python_nocache": "#63b3ed",
    "ruby_cache": "#9b2c2c",
    "ruby_nocache": "#fc8181",
}


def carregar_dados(pasta: Path):
    """Retorna dados[cenario][usuarios] = dict_linha_aggregated."""
    dados = defaultdict(dict)
    for arq in sorted(pasta.glob("*_stats.csv")):
        m = PADRAO_ARQ.fullmatch(arq.name)
        if not m:
            continue
        cenario, usuarios = m.group(1), int(m.group(2))
        with open(arq, newline="", encoding="utf-8") as f:
            agg = next((r for r in csv.DictReader(f) if r["Name"] == "Aggregated"), None)
        if agg:
            dados[cenario][usuarios] = agg
    return dados


def plotar_metrica(dados, metrica_nome, metrica_label, unidade, fn_valor, saida: Path):
    cenarios = [c for c in ["python_cache", "python_nocache", "ruby_cache", "ruby_nocache"] if c in dados]
    todos_usuarios = sorted({u for c in cenarios for u in dados[c]})

    if not todos_usuarios:
        return

    largura_fig = max(9.0, 2.0 * len(todos_usuarios))
    fig, ax = plt.subplots(figsize=(largura_fig, 5.5))

    largura = 0.18
    import numpy as np
    x = np.arange(len(todos_usuarios))

    for idx, cenario in enumerate(cenarios):
        valores = [fn_valor(dados[cenario].get(u, {"v": 0})) for u in todos_usuarios]
        pos = x + (idx - (len(cenarios) - 1) / 2) * largura
        ax.bar(pos, valores, largura, label=ROTULOS.get(cenario, cenario), color=CORES.get(cenario))

    ax.set_title(f"Link Extractor: {metrica_label}", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Número de Usuários Virtuais Simultâneos", fontsize=11)
    ax.set_ylabel(f"{metrica_label} ({unidade})", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{u} usuários" for u in todos_usuarios])
    ax.legend(frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    fig.tight_layout()
    fig.savefig(saida, dpi=150)
    plt.close(fig)
    print(f"Gráfico gerado: {saida.name}")


def plotar_percentis(dados, saida: Path):
    percentis_cols = ["50%", "66%", "75%", "80%", "90%", "95%", "98%", "99%"]
    cenarios = [c for c in ["python_cache", "python_nocache", "ruby_cache", "ruby_nocache"] if c in dados]
    todos_usuarios = sorted({u for c in cenarios for u in dados[c]})

    if not todos_usuarios:
        return

    fig, axes = plt.subplots(1, len(todos_usuarios), figsize=(4.0 * len(todos_usuarios), 4.5), sharey=True)
    if len(todos_usuarios) == 1:
        axes = [axes]

    for ax, u in zip(axes, todos_usuarios):
        for cenario in cenarios:
            linha = dados[cenario].get(u)
            if linha:
                ys = [float(linha[p]) for p in percentis_cols]
                ax.plot(range(len(percentis_cols)), ys, marker="o", label=ROTULOS.get(cenario, cenario),
                        color=CORES.get(cenario), linewidth=2)
        ax.set_title(f"{u} usuários", fontsize=12, fontweight="bold")
        ax.set_xlabel("Percentil", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_xticks(range(len(percentis_cols)))
        ax.set_xticklabels(percentis_cols, rotation=45)

    axes[0].set_ylabel("Tempo de Resposta (ms)", fontsize=11)
    axes[-1].legend(loc="upper left")
    fig.suptitle("Distribuição de Percentis do Tempo de Resposta", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(saida, dpi=150)
    plt.close(fig)
    print(f"Gráfico gerado: {saida.name}")


def gerar_tabela_resumo(dados, saida_md: Path):
    linhas = []
    linhas.append("# Resumo de Desempenho - Trabalho 4 (Link Extractor)\n")
    linhas.append("| Cenário | Usuários | Reqs | Falhas | Tempo Médio (ms) | Mediana p50 (ms) | p90 (ms) | p95 (ms) | RPS (req/s) |")
    linhas.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    cenarios = [c for c in ["python_cache", "python_nocache", "ruby_cache", "ruby_nocache"] if c in dados]
    for c in cenarios:
        for u in sorted(dados[c]):
            r = dados[c][u]
            linhas.append(
                f"| {ROTULOS.get(c, c)} | {u} | {r['Request Count']} | {r['Failure Count']} | "
                f"{float(r['Average Response Time']):.1f} | {float(r['50%']):.1f} | "
                f"{float(r['90%']):.1f} | {float(r['95%']):.1f} | {float(r['Requests/s']):.1f} |"
            )

    saida_md.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Tabela resumo gerada: {saida_md.name}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", type=Path, default=ROOT / "results")
    ap.add_argument("--out", type=Path, default=ROOT / "graficos")
    args = ap.parse_args()

    dados = carregar_dados(args.results)
    if not dados:
        print(f"Nenhum arquivo *_stats.csv encontrado em {args.results}. Execute scripts/run_all.py primeiro.")
        return

    args.out.mkdir(exist_ok=True)

    plotar_metrica(
        dados, "tempo_medio", "Tempo Médio de Resposta", "ms",
        lambda r: float(r.get("Average Response Time", 0)),
        args.out / "tempo_medio.png"
    )

    plotar_metrica(
        dados, "mediana_p50", "Mediana do Tempo de Resposta (p50)", "ms",
        lambda r: float(r.get("50%", 0)),
        args.out / "mediana_p50.png"
    )

    plotar_metrica(
        dados, "percentil_95", "Tempo de Resposta Percentil 95 (p95)", "ms",
        lambda r: float(r.get("95%", 0)),
        args.out / "percentil_95.png"
    )

    plotar_metrica(
        dados, "req_por_segundo", "Taxa de Requisições por Segundo (Throughput)", "req/s",
        lambda r: float(r.get("Requests/s", 0)),
        args.out / "req_por_segundo.png"
    )

    plotar_percentis(dados, args.out / "curva_percentis.png")
    gerar_tabela_resumo(dados, args.out / "tabela_resumo.md")


if __name__ == "__main__":
    main()
