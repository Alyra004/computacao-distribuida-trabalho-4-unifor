# Trabalho 4 – Realização de Testes de Desempenho com a Aplicação Link Extractor

Trabalho 4 da disciplina de Computação Distribuída (UNIFOR): realizar testes de desempenho com as duas versões do serviço de extração de link (**Python** e **Ruby**), avaliando o comportamento da arquitetura **com e sem serviço de cache (Redis)** sob diferentes cargas de usuários virtuais geradas pelo **Locust**.

---

## Equipe

| Nome | Matrícula |
|---|---|
| João Igor Vidal de Andrade | 2320296 |
| Raquel Albuquerque Quirino | 2320325 |
| Amanda Lira Andrade Botelho | 2320291 |

---

## 1. Sobre o Projeto

A aplicação **Link Extractor** oferece um serviço web para extrair e exibir hiperlinks contidos em páginas web. A arquitetura segue o modelo de microsserviços containerizados com Docker:
- **Front-end Web**: Interface construída em **PHP (Apache)** onde o usuário informa a URL a ser analisada.
- **Serviço de Extração de Links (API)**: Disponível em duas implementações:
  1. **Python (Flask + BeautifulSoup + Gunicorn)** escutando na porta `5000`.
  2. **Ruby (Sinatra + Nokogiri + Puma)** escutando na porta `4567`.
- **Serviço de Cache**: **Redis** (`6379`), que acelera as requisições evitando reprocessamento de URLs já consultadas.
- **Gerador de Carga**: **Locust** (`8089`), responsável por emular múltiplos usuários virtuais executando a sequência de requisições.
- **Mock Target**: Servidor Nginx local servindo 10 páginas HTML estáticas locais (`http://mock-target/page1.html` a `page10.html`) para garantir testes determinísticos, controlados e sem interferência de instabilidades de rede externa ou bloqueios de rate limit de sites da internet.

---

## 2. Cenários de Teste Avaliados

A bateria de testes avalia 4 combinações arquiteturais sob três patamares de usuários virtuais simultâneos (ex.: **10, 50 e 100 usuários**):

| Cenário | Linguagem da API | Cache Redis | Alvo do Locust |
|---|---|---|---|
| **1. Python com Cache** | Python (Flask/Gunicorn) | Ativado (`ENABLE_CACHE=true`) | `http://api-python:5000` |
| **2. Python sem Cache** | Python (Flask/Gunicorn) | Desativado (`ENABLE_CACHE=false`) | `http://api-python:5000` |
| **3. Ruby com Cache** | Ruby (Sinatra/Puma) | Ativado (`ENABLE_CACHE=true`) | `http://api-ruby:4567` |
| **4. Ruby sem Cache** | Ruby (Sinatra/Puma) | Desativado (`ENABLE_CACHE=false`) | `http://api-ruby:4567` |

---

## 3. Comportamento do Usuário Virtual (Locust)

Em conformidade com a especificação do trabalho:
- Cada usuário virtual executa rigorosamente um `SequentialTaskSet` com uma **sequência de 10 invocações** ao serviço de extração de link (`/api/<URL>`).
- Em cada invocação é enviada uma URL distinta:
  - `http://mock-target/page1.html`
  - `http://mock-target/page2.html`
  - ... até `http://mock-target/page10.html`
- No modo **com cache**: a primeira requisição gera cache miss e popula o Redis; as requisições seguintes resultam em cache hit imediato.
- No modo **sem cache**: todas as requisições forçam a raspagem e o parsing completo do HTML.

---

## 4. Estrutura de Arquivos

```
├── api-python/              # API em Python (Flask + BeautifulSoup)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── linkextractor.py
│   └── main.py
├── api-ruby/                # API em Ruby (Sinatra + Nokogiri)
│   ├── Dockerfile
│   ├── Gemfile
│   └── linkextractor.rb
├── web/                     # Front-end PHP
│   ├── Dockerfile
│   └── index.php
├── mock-server/             # Mock de 10 páginas HTML para testes estáveis
│   └── html/page1..10.html
├── locust/                  # Configuração do Locust
│   └── locustfile.py        # Sequência das 10 requisições
├── scripts/
│   ├── run_all.py           # Automação completa de todos os testes
│   └── plot.py              # Geração dos gráficos e tabela resumo
├── docker-compose.yml       # Orquestração de todos os serviços
├── results/                 # CSVs brutos gerados pelo Locust
└── graficos/                # Figuras e tabelas para o Google Slides
```

---

## 5. Como Executar

### 5.1 Subir o ambiente com Docker Compose
```bash
docker compose up -d --build
```

Serviços disponíveis após inicialização:
- **Web Frontend (PHP)**: `http://localhost:8080`
- **API Python**: `http://localhost:5000/api/http://mock-target/page1.html`
- **API Ruby**: `http://localhost:4567/api/http://mock-target/page1.html`
- **Locust Web UI**: `http://localhost:8089`

### 5.2 Executar a bateria automatizada de testes
Para rodar todos os cenários e cargas automaticamente:
```bash
python scripts/run_all.py
```

Opções úteis:
```bash
# Execução rápida para teste preliminar
python scripts/run_all.py --users 10 --duration 15

# Forçar reexecução mesmo se já houver resultados salvos
python scripts/run_all.py --force
```

### 5.3 Gerar os gráficos e tabelas
Após a conclusão dos testes:
```bash
python scripts/plot.py
```
Os arquivos gerados serão salvos na pasta `graficos/`:
- `tempo_medio.png`
- `mediana_p50.png`
- `percentil_95.png`
- `req_por_segundo.png`
- `curva_percentis.png`
- `tabela_resumo.md`
