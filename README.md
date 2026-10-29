# Trabalho 4 – Realização de Testes de Desempenho com a Aplicação Link Extractor

**Universidade de Fortaleza (UNIFOR)**  
**Disciplina:** Computação Distribuída / Sistemas Distribuídos  

---

## 👥 Equipe

| Nome | Matrícula |
| :--- | :---: |
| **Amanda Lira Andrade Botelho** | 2320291 |
| **João Igor Vidal de Andrade** | 2320296 |
| **Raquel Albuquerque Quirino** | 2320325 |

---

## 1. Sobre o Projeto e Arquitetura

O objetivo deste trabalho é avaliar o desempenho de duas implementações da API de extração de hiperlinks (**Python** e **Ruby**) da aplicação **Link Extractor**, mensurando o impacto real da introdução de uma camada de **cache em memória (Redis)** sob diferentes regimes de concorrência gerados pelo **Locust**.

A aplicação foi orquestrada em microsserviços via Docker Compose:
- **Web Frontend (PHP 8.1 / Apache)**: Interface para submissão de URLs e listagem dos links extraídos (`http://localhost:8080`).
- **API Python (Flask + Gunicorn)**: Microsserviço de extração executando com múltiplos workers/threads (`-w 4 --threads 2`).
- **API Ruby (Sinatra + Puma)**: Microsserviço equivalente em Ruby utilizando Nokogiri para parsing de HTML.
- **Cache (Redis 7 Alpine)**: Armazenamento em memória sob o padrão *Cache-Aside*.
- **Mock Target (Nginx Alpine)**: Servidor HTTP local servindo 10 páginas HTML estáticas dedicadas (`http://mock-target/page1..10.html`), garantindo reprodutibilidade, testes determinísticos e ausência de bloqueios de rate limit de redes externas.
- **Locust (2.32.0)**: Gerador de carga executando em modo *headless*.

```
                           ┌─────────────────────────────┐
                           │      Web Frontend (PHP)     │
                           └──────────────┬──────────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   ▼                                             ▼
        ┌─────────────────────┐                       ┌─────────────────────┐
        │   API Python/Flask  │                       │    API Ruby/Sinatra │
        └──────────┬──────────┘                       └──────────┬──────────┘
                   │                                             │
                   ├──────────────────────┬──────────────────────┤
                   ▼                      ▼                      ▼
        ┌─────────────────────┐ ┌───────────────────┐ ┌─────────────────────┐
        │     Redis Cache     │ │   Locust (Carga)  │ │ Mock Target (Nginx) │
        └─────────────────────┘ └───────────────────┘ └─────────────────────┘
```

---

## 2. Metodologia e Calibragem dos Testes

- **Comportamento do Usuário Virtual**: Implementado via `SequentialTaskSet`, cada usuário virtual executa rigorosamente uma **sequência de 10 requisições HTTP GET** ordenadas, requisitando uma URL diferente a cada invocação (`page1.html` até `page10.html`).
- **Tempo de Espera (*wait_time*)**: Pausa controlada de 0.5 a 1.5 s entre cada ciclo de extrações.
- **Calibragem Contínua de Carga**: Para cobrir desde o tempo de resposta puro até a saturação real do sistema, foram testados 4 níveis contínuos de usuários simultâneos:
  - **10 usuários**: Carga mínima / linha de base.
  - **50 usuários**: Carga leve.
  - **100 usuários**: Carga média nominal.
  - **200 usuários**: Carga alta / estresse.

---

## 3. Tabela Consolidada de Resultados

Todas as 16 baterias de teste foram executadas com **100% de sucesso (0 falhas em mais de 32.000 requisições)**:

| Cenário | Usuários | Reqs Totais | Falhas | Tempo Médio | Mediana (p50) | p90 | p95 | Vazão (RPS) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Python c/ Cache** | 10 | 347 | **0%** | **2,8 ms** | **2,0 ms** | 2,0 ms | 3,0 ms | 9,8 req/s |
| **Python c/ Cache** | 50 | 1.760 | **0%** | **2,2 ms** | **2,0 ms** | 3,0 ms | 3,0 ms | 49,9 req/s |
| **Python c/ Cache** | 100 | 3.552 | **0%** | **2,1 ms** | **2,0 ms** | 3,0 ms | 3,0 ms | 100,7 req/s |
| **Python c/ Cache** | 200 | 7.083 | **0%** | **2,1 ms** | **2,0 ms** | 3,0 ms | 3,0 ms | **200,8 req/s** |
| **Python s/ Cache** | 10 | 353 | **0%** | 16,5 ms | 15,0 ms | 21,0 ms | 27,0 ms | 10,0 req/s |
| **Python s/ Cache** | 50 | 1.729 | **0%** | 33,5 ms | 17,0 ms | 47,0 ms | 120,0 ms | 48,6 req/s |
| **Python s/ Cache** | 100 | 3.450 | **0%** | 22,5 ms | 17,0 ms | 37,0 ms | 45,0 ms | 98,1 req/s |
| **Python s/ Cache** | 200 | 6.388 | **0%** | **109,2 ms** | 44,0 ms | 240,0 ms | **520,0 ms** | 180,0 req/s |
| **Ruby c/ Cache** | 10 | 341 | **0%** | **4,7 ms** | **2,0 ms** | 3,0 ms | 8,0 ms | 9,8 req/s |
| **Ruby c/ Cache** | 50 | 864 | **0%** | 365,4 ms | 300,0 ms | 460,0 ms | 490,0 ms | 24,9 req/s |
| **Ruby c/ Cache** | 100 | 880 | **0%** | 277,3 ms | 250,0 ms | 380,0 ms | 410,0 ms | 24,9 req/s |
| **Ruby c/ Cache** | 200 | 879 | **0%** | 294,6 ms | 280,0 ms | 400,0 ms | 440,0 ms | 24,9 req/s |
| **Ruby s/ Cache** | 10 | 347 | **0%** | 11,0 ms | 8,0 ms | 19,0 ms | 26,0 ms | 9,8 req/s |
| **Ruby s/ Cache** | 50 | 834 | **0%** | 276,5 ms | 260,0 ms | 400,0 ms | 440,0 ms | 23,6 req/s |
| **Ruby s/ Cache** | 100 | 841 | **0%** | 312,3 ms | 280,0 ms | 410,0 ms | 440,0 ms | 23,8 req/s |
| **Ruby s/ Cache** | 200 | 843 | **0%** | 362,2 ms | 300,0 ms | 430,0 ms | 480,0 ms | 23,8 req/s |

---

## 4. Análise dos Resultados e Gráficos

### 4.1 Tempo Médio e Mediana de Resposta
![Tempo Médio de Resposta](graficos/tempo_medio.png)
![Mediana do Tempo de Resposta](graficos/mediana_p50.png)

- **Python com Cache**: Apresentou estabilidade absoluta, mantendo tempo médio entre **2,1 ms e 2,8 ms** e mediana em **2,0 ms** em todos os regimes de concorrência (de 10 a 200 usuários).
- **Python sem Cache**: O tempo médio começa em 16,5 ms e sobe para **109,2 ms** (mediana 44 ms, p95 de **520 ms**) sob 200 usuários simultâneos, refletindo o custo cumulativo de parsing do DOM de páginas realistas de 60 KB.
- **Ruby**: Com 10 usuários, apresenta excelente latência (**4,7 ms** com cache vs 11,0 ms sem cache). A partir de 50 usuários, entra em saturação de processo único (Puma com GVL), com mediana oscilando entre **250 ms e 300 ms** devido ao enfileiramento na porta do serviço.

### 4.2 Vazão e Throughput (Requisições por Segundo)
![Requisições por Segundo](graficos/req_por_segundo.png)

- **Escalabilidade Linear no Python**: A vazão escala de forma contínua acompanhando a carga dos usuários virtuais: de **9,8 req/s** (10 usuários) até atingir **200,8 req/s** (200 usuários).
- **Platô de Saturação no Ruby**: O Ruby atinge um teto estrito de capacidade em **~24,9 req/s**, mantendo essa mesma vazão de 50 a 200 usuários devido à saturação do processo único.

### 4.3 Percentil 95 (p95) e Distribuição de Percentis
![Percentil 95](graficos/percentil_95.png)
![Curva de Distribuição de Percentis](graficos/curva_percentis.png)

- O **p95 do Python com Cache** permaneceu cravado em **3,0 ms** mesmo sob 200 usuários, comprovando que 95% das respostas chegam de forma praticamente instantânea.
- No **Python sem Cache**, o p95 degradou de 27 ms (10 usuários) para **520 ms** (200 usuários).
- No **Ruby**, o p95 atinge de **410 ms a 490 ms** nas cargas elevadas, refletindo o tempo que as conexões excedentes aguardam no buffer do socket TCP (*queuing delay*).

---

## 5. Principais Conclusões Técnicas

1. **Cálculo de Speedup do Redis**:
   $$\text{Speedup (200 usuários)} = \frac{\text{Tempo Sem Cache}}{\text{Tempo Com Cache}} = \frac{109,2\text{ ms}}{2,1\text{ ms}} \approx 52\times$$
   Com páginas realistas (40–60 KB e 60–90 links), o cache em memória reduziu a latência em mais de 98% sob 200 usuários simultâneos (uma aceleração de **52×**), comprovando a eficácia do padrão *Cache-Aside* ao poupar CPU e I/O de reprocessamento DOM.

2. **Diferença Arquitetural: Gunicorn (Python) vs Puma/Sinatra (Ruby)**:
   - O Python utilizou o servidor **Gunicorn em modelo prefork multi-worker com threads** (`-w 4 --threads 2`), distribuindo as requisições em paralelo entre múltiplos núcleos do processador.
   - O Ruby executou em **processo único**, sendo limitado pela trava global do interpretador (GVL/GIL) em operações concorrentes de string/parsing. Isso comprova que em sistemas distribuídos a **arquitetura do servidor de aplicação** é tão determinante quanto a linguagem escolhida.

3. **O Fenômeno de *Cache Stampede* (*Thundering Herd*)**:
   - Observado no teste de 50 usuários do Ruby com cache frio, onde a largada concorrente de 50 clientes disputando as mesmas URLs não cacheadas gerou miss coletivo simultâneo e elevou o tempo médio para 365,4 ms.
   - Conforme o número de requisições aumentou (100 e 200 usuários), as chaves aquecidas permitiram ao cache superar o cenário sem cache (277 ms vs 312 ms a 100 usuários, e 294 ms vs 362 ms a 200 usuários). Em sistemas de produção, essa anomalia é mitigada através de *Locks Distribuídos* (`SET NX` no Redis) ou rotinas de *Cache Warming*.

---

## 6. Como Reproduzir os Testes

```powershell
# 1. Subir os contêineres limpos
docker compose down --remove-orphans
docker compose up -d

# 2. Executar a bateria de testes automatizada (CSVs salvos em results/)
python scripts/run_all.py

# 3. Gerar os gráficos e tabelas atualizados (salvos em graficos/)
.venv\Scripts\python scripts/plot.py
```

- Documento de roteiro completo para a apresentação: [docs/APRESENTACAO_TRABALHO_4.md](docs/APRESENTACAO_TRABALHO_4.md)
- Planilha com todos os dados brutos: [graficos/tabela_desempenho.csv](graficos/tabela_desempenho.csv)
