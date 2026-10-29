#!/usr/bin/env python3
"""Gera 10 páginas HTML realistas e ricas no mock-server/html/.
Cada página possui entre 50 KB e 80 KB de HTML com 60 a 90 links (<a>)
distribuídos em menus, artigos, seções, tabelas e rodapés estilo Wikipedia.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOCK_DIR = ROOT / "mock-server" / "html"

TEMAS = [
    ("Computação Distribuída", "Sistemas Distribuídos, Consenso e Arquiteturas P2P"),
    ("Arquitetura de Microsserviços", "Padrões de Projeto, Service Mesh e Resiliência"),
    ("Cache em Sistemas Modernos", "Estratégias de Cache-Aside, Write-Through e Invalidação"),
    ("Virtualização e Contêineres", "Kernel Namespaces, Cgroups e Isolamento com Docker"),
    ("Bancos de Dados NoSQL e Redis", "Armazenamento em Memória, Estruturas de Dados e TTL"),
    ("Protocolos de Rede e HTTP/2", "Multiplexação, Latência, TCP Congestion e WebSockets"),
    ("Balanceamento de Carga", "Algoritmos Round-Robin, Least Connections e Consistent Hashing"),
    ("Testes de Carga e Performance", "Métricas de Throughput, Percentis de Latência e Stress Testing"),
    ("Modelos de Concorrência", "Multi-Threading, Multi-Processing e Event Loops Assíncronos"),
    ("Alta Disponibilidade e Tolerância a Falhas", "Replicação de Dados, Quorum e Recuperação de Desastres")
]

PARAGRAFO_BASE = (
    "A computação moderna exige que sistemas distribuídos processem volumes massivos de requisições "
    "mantendo baixa latência e alta tolerância a falhas. O particionamento de carga através de microsserviços "
    "desacoplados permite escalar horizontalmente componentes críticos, enquanto camadas de cache em memória "
    "como o Redis reduzem drasticamente o consumo de CPU ao evitar processamento repetitivo de parsing e extração. "
    "A análise empírica do tempo de resposta demonstra como variações em algoritmos de agendamento e servidores "
    "de aplicação impactam a estabilidade global da infraestrutura sob regimes de concorrência intensa.\n\n"
)

def gerar_pagina(indice: int, titulo: str, subtitulo: str) -> str:
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang=\"pt-BR\">")
    html.append("<head>")
    html.append(f"  <meta charset=\"UTF-8\">")
    html.append(f"  <title>{titulo} - Enciclopédia de Sistemas Distribuídos</title>")
    html.append("  <style>body{font-family:sans-serif;line-height:1.6;margin:30px}nav a,footer a{margin-right:12px}</style>")
    html.append("</head>")
    html.append("<body>")
    html.append("  <header>")
    html.append(f"    <h1>{titulo}</h1>")
    html.append(f"    <h3>{subtitulo}</h3>")
    html.append("  </header>")

    # 1. Menu de Navegação Superior (10 links)
    html.append("  <nav id=\"toc\">")
    html.append("    <h4>Índice de Artigos Relacionados:</h4>")
    html.append("    <ul>")
    for i, (t, _) in enumerate(TEMAS, 1):
        html.append(f"      <li><a href=\"http://mock-target/page{i}.html\">Artigo {i}: {t}</a></li>")
    html.append("    </ul>")
    html.append("  </nav>")
    html.append("  <hr>")

    # 2. Conteúdo Principal com Artigo Longo e Links embutidos (cerca de 50 links)
    html.append("  <main>")
    for secao in range(1, 8):
        html.append(f"    <section id=\"secao-{secao}\">")
        html.append(f"      <h2>Seção {secao}: Aprofundamento Teórico em {titulo} (Parte {secao})</h2>")
        html.append(f"      <p>{PARAGRAFO_BASE * 3}</p>")
        html.append("      <p>Veja tópicos complementares e fontes primárias:</p>")
        html.append("      <ul>")
        for k in range(1, 8):
            target_page = ((indice + secao + k) % 10) + 1
            html.append(f"        <li>Referência técnica: <a href=\"http://mock-target/page{target_page}.html#ref-{secao}-{k}\">Documentação de Estudo {secao}.{k} sobre {titulo}</a></li>")
            html.append(f"        <li>Link externo complementar: <a href=\"https://www.w3.org/Protocols/rfc2616/rfc2616-sec{secao}.html#item-{k}\">Especificação W3C RFC 2616 Seção {secao}.{k}</a></li>")
        html.append("      </ul>")
        html.append("    </section>")
        html.append("    <hr>")

    # 3. Seção de Tabela de Dados e Recursos (cerca de 15 links)
    html.append("    <section id=\"tabela-recursos\">")
    html.append("      <h2>Recursos e Ferramentas Recomendadas</h2>")
    html.append("      <table border=\"1\" cellpadding=\"8\" cellspacing=\"0\">")
    html.append("        <tr><th>Tecnologia</th><th>Documentação</th><th>Código Fonte</th></tr>")
    ferramentas = ["Docker", "Redis", "Locust", "Nginx", "Python-Flask", "Ruby-Sinatra", "Gunicorn", "Puma"]
    for f in ferramentas:
        html.append(f"        <tr><td>{f}</td><td><a href=\"https://docs.example.org/{f.lower()}/guide\">Manual {f}</a></td><td><a href=\"https://github.com/example/{f.lower()}-project\">Repositório {f}</a></td></tr>")
    html.append("      </table>")
    html.append("    </section>")
    html.append("  </main>")
    html.append("  <hr>")

    # 4. Rodapé Extenso com Metadados e Links de Referência (mais 15 links)
    html.append("  <footer>")
    html.append("    <p>Portal Acadêmico de Sistemas Distribuídos - UNIFOR 2026</p>")
    html.append("    <p>")
    for r in range(1, 16):
        html.append(f"      <a href=\"http://mock-target/page{(r % 10) + 1}.html#rodape-{r}\">Termo {r}</a> |")
    html.append("    </p>")
    html.append("  </footer>")
    html.append("</body>")
    html.append("</html>")
    return "\n".join(html)

def main():
    MOCK_DIR.mkdir(parents=True, exist_ok=True)
    print("Gerando 10 páginas HTML realistas e pesadas em mock-server/html/ ...")
    for i, (titulo, subtitulo) in enumerate(TEMAS, 1):
        conteudo = gerar_pagina(i, titulo, subtitulo)
        arquivo = MOCK_DIR / f"page{i}.html"
        arquivo.write_text(conteudo, encoding="utf-8")
        num_links = conteudo.count("<a ")
        tamanho_kb = len(conteudo.encode("utf-8")) / 1024
        print(f"  [OK] page{i}.html: {tamanho_kb:.1f} KB com {num_links} links hipertexto!")
    print("\nPáginas realistas geradas com sucesso!")

if __name__ == "__main__":
    main()

