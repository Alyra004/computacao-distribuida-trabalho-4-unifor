#!/usr/bin/env python3
"""Roda a bateria de testes de desempenho do Trabalho 4 (Link Extractor):
Combinações:
  - Linguagem: Python vs Ruby
  - Cache: Com Cache (Redis) vs Sem Cache
  - Usuários Virtuais: 10, 50, 100, 200, 300

Total de 4 cenários:
  1. python_cache   (http://api-python-cache:5000)
  2. python_nocache (http://api-python-nocache:5000)
  3. ruby_cache     (http://api-ruby-cache:4567)
  4. ruby_nocache   (http://api-ruby-nocache:4567)
"""
import argparse
import csv
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

# Progressão completa: desde carga leve (10) até carga de estresse real (200, 300)
USERS = [10, 50, 100, 200, 300]
DURATION = 35      # segundos de medição estável
RAMP = 5           # segundos de rampa de subida dos usuários

SCENARIOS_CONFIG = {
    "python_cache": {
        "target": "http://api-python-cache:5000",
        "desc": "Python c/ Cache Redis"
    },
    "python_nocache": {
        "target": "http://api-python-nocache:5000",
        "desc": "Python s/ Cache"
    },
    "ruby_cache": {
        "target": "http://api-ruby-cache:4567",
        "desc": "Ruby c/ Cache Redis"
    },
    "ruby_nocache": {
        "target": "http://api-ruby-nocache:4567",
        "desc": "Ruby s/ Cache"
    },
}


def compose(*args, check=True, capture=False):
    return subprocess.run(
        ["docker", "compose", *args], cwd=ROOT, check=check,
        capture_output=capture, text=True,
    )


def limpar_redis():
    """Limpa o Redis para testes em estado inicial conhecido."""
    try:
        compose("exec", "-T", "redis", "redis-cli", "flushall", check=False, capture=True)
    except Exception:
        pass


def resumo(prefixo):
    csv_file = RESULTS / f"{prefixo}_stats.csv"
    if not csv_file.exists():
        return "sem dados"
    with open(csv_file, newline="", encoding="utf-8") as f:
        agg = next((r for r in csv.DictReader(f) if r["Name"] == "Aggregated"), None)
    if not agg:
        return "estatísticas agregadas não encontradas"
    reqs = agg.get("Request Count", "0")
    fails = agg.get("Failure Count", "0")
    avg = float(agg.get("Average Response Time", 0))
    p50 = float(agg.get("50%", 0))
    p95 = float(agg.get("95%", 0))
    rps = float(agg.get("Requests/s", 0))
    return (
        f"{reqs} reqs, {fails} falhas, "
        f"Média: {avg:.1f} ms, "
        f"Mediana: {p50:.1f} ms, "
        f"p95: {p95:.1f} ms, "
        f"RPS: {rps:.1f} req/s"
    )


def rodar_teste(scenario_key, usuarios, duracao, force):
    prefixo = f"{scenario_key}_u{usuarios}"
    csv_file = RESULTS / f"{prefixo}_stats.csv"

    if csv_file.exists() and not force:
        print(f"[PULA] {prefixo} (já concluído): {resumo(prefixo)}", flush=True)
        return

    cfg = SCENARIOS_CONFIG[scenario_key]
    spawn_rate = max(1, usuarios // RAMP)
    print(f"[RODA] {prefixo} ({usuarios} usuários) ...", end=" ", flush=True)

    # Limpa cache do Redis se for cenário com cache
    if "cache" in scenario_key and "nocache" not in scenario_key:
        limpar_redis()

    r = compose(
        "run", "--rm", "-T",
        "-e", "USE_MOCK_TARGET=true",
        "locust",
        "--headless", "-u", str(usuarios), "-r", str(spawn_rate),
        "-t", f"{RAMP + duracao}s",
        "-H", cfg["target"],
        "--reset-stats",
        "--csv", f"/mnt/results/{prefixo}", "--only-summary",
        capture=True, check=False,
    )

    if not csv_file.exists():
        print(f"\nErro: Locust não gerou CSV para {prefixo} (código {r.returncode}):\n{r.stderr[-1500:]}")
    else:
        print(resumo(prefixo), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--users", type=int, nargs="+", default=USERS, help="Lista de usuários virtuais")
    ap.add_argument("--scenarios", type=str, nargs="+", default=list(SCENARIOS_CONFIG.keys()),
                    choices=list(SCENARIOS_CONFIG.keys()), help="Cenários a executar")
    ap.add_argument("--duration", type=int, default=DURATION, help="Segundos medidos por execução")
    ap.add_argument("--force", action="store_true", help="Refaz execuções que já possuem CSV")
    args = ap.parse_args()

    RESULTS.mkdir(exist_ok=True)

    print("Garantindo que todos os contêineres estejam iniciados...")
    compose("up", "-d")
    time.sleep(1)

    print(f"\nBateria de testes configurada para usuários: {args.users}")

    for scen in args.scenarios:
        cfg = SCENARIOS_CONFIG[scen]
        print(f"\n--> Cenário: {cfg['desc']} ({scen})")
        for u in args.users:
            rodar_teste(scen, u, args.duration, args.force)

    print("\nBateria de testes finalizada! Resultados salvos em results/.")


if __name__ == "__main__":
    main()
