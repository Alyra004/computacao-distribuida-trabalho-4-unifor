# Roteiro da Apresentação – Trabalho 4 (Link Extractor)
**Universidade de Fortaleza (UNIFOR) – Computação Distribuída**  
**Equipe:** Amanda Lira Andrade Botelho (2320291), João Igor Vidal de Andrade (2320296), Raquel Albuquerque Quirino (2320325)

---

## Slide 1: Capa
- **Título:** Avaliação de Desempenho e Caching em Microsserviços com a Aplicação Link Extractor
- **Subtítulo:** Análise Comparativa entre Python e Ruby com Cache Redis sob Testes de Carga com Locust
- **Equipe:** Amanda Lira Andrade Botelho, João Igor Vidal de Andrade, Raquel Albuquerque Quirino
- **Instituição:** Universidade de Fortaleza (UNIFOR) – Computação Distribuída

---

## Slide 2: Contextualização e Objetivos
- **Contexto:** Microsserviços modernos de extração de dados web enfrentam alto custo de I/O e processamento intensivo de parsing DOM.
- **Objetivo Principal:** Avaliar o impacto da adoção de uma camada de cache em memória (*Cache-Aside* com Redis) sobre a latência e a vazão.
- **Comparativo:** Duas implementações de API (Python/Flask com Gunicorn vs. Ruby/Sinatra com Puma).
- **Abordagem Científica:** Cargas sintéticas controladas com Locust sob páginas HTML realistas (40–60 KB, 60–90 links cada).

---

## Slide 3: Arquitetura da Solução
- **Componentes Orquestrados via Docker Compose:**
  - **Web Frontend (PHP 8.1 / Apache):** Interface web para o usuário final submeter URLs e visualizar resultados.
  - **API Python (Flask + Gunicorn):** Microsserviço escalado em 4 workers e 2 threads por worker (`-w 4 --threads 2`).
  - **API Ruby (Sinatra + Puma):** Microsserviço Nokogiri com servidor web Puma.
  - **Camada de Cache (Redis 7 Alpine):** Armazenamento chave-valor em memória RAM sob o padrão *Cache-Aside*.
  - **Mock Target (Nginx Alpine):** Servidor HTTP local servindo 10 páginas estáticas pesadas (`page1.html` a `page10.html`), garantindo repetibilidade e isolamento de rede externa.
  - **Locust (Headless):** Gerador de carga com métricas exportadas em CSV.

---

## Slide 4: Metodologia de Testes e Calibragem
- **Comportamento Sequencial (`SequentialTaskSet`):** Cada usuário virtual executa rigorosamente um ciclo ordenado de 10 requisições (`page1.html` até `page10.html`).
- **Intervalo de Pausa Controlado:** `wait_time` de 0.5 a 1.5 s entre ciclos.
- **Calibragem dos Níveis de Concorrência:**
  - **10 Usuários:** Linha de base (baseline / baixa carga).
  - **50 Usuários:** Carga moderada.
  - **100 Usuários:** Carga média nominal.
  - **200 Usuários:** Alta concorrência / estresse.
- **Total:** 16 baterias de testes (4 cenários × 4 patamares de carga), com limpeza de cache (`FLUSHALL`) antes de cada teste com cache.

---

## Slide 5: Tabela Consolidada de Desempenho
- **Tabela Resumo (0% de Falha em todas as 32.000+ requisições):**

| Cenário | Usuários | Tempo Médio | Mediana (p50) | p95 | RPS (Vazão) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Python c/ Cache** | 10 | 2,8 ms | 2,0 ms | 3,0 ms | 9,8 req/s |
| **Python c/ Cache** | 50 | 2,2 ms | 2,0 ms | 3,0 ms | 49,9 req/s |
| **Python c/ Cache** | 100 | 2,1 ms | 2,0 ms | 3,0 ms | 100,7 req/s |
| **Python c/ Cache** | 200 | **2,1 ms** | **2,0 ms** | **3,0 ms** | **200,8 req/s** |
| **Python s/ Cache** | 10 | 16,5 ms | 15,0 ms | 27,0 ms | 10,0 req/s |
| **Python s/ Cache** | 50 | 33,5 ms | 17,0 ms | 120,0 ms | 48,6 req/s |
| **Python s/ Cache** | 100 | 22,5 ms | 17,0 ms | 45,0 ms | 98,1 req/s |
| **Python s/ Cache** | 200 | **109,2 ms** | **44,0 ms** | **520,0 ms** | 180,0 req/s |
| **Ruby c/ Cache** | 10 | 4,7 ms | 2,0 ms | 8,0 ms | 9,8 req/s |
| **Ruby c/ Cache** | 50 | 365,4 ms | 300,0 ms | 490,0 ms | 24,9 req/s |
| **Ruby c/ Cache** | 100 | 277,3 ms | 250,0 ms | 410,0 ms | 24,9 req/s |
| **Ruby c/ Cache** | 200 | 294,6 ms | 280,0 ms | 440,0 ms | 24,9 req/s |
| **Ruby s/ Cache** | 10 | 11,0 ms | 8,0 ms | 26,0 ms | 9,8 req/s |
| **Ruby s/ Cache** | 50 | 276,5 ms | 260,0 ms | 440,0 ms | 23,6 req/s |
| **Ruby s/ Cache** | 100 | 312,3 ms | 280,0 ms | 440,0 ms | 23,8 req/s |
| **Ruby s/ Cache** | 200 | 362,2 ms | 300,0 ms | 480,0 ms | 23,8 req/s |

---

## Slide 6: Análise de Latência (Tempo Médio e Mediana)
- `[INSERIR IMAGEM: graficos/tempo_medio.png]`
- `[INSERIR IMAGEM: graficos/mediana_p50.png]`
- **Destaques:**
  - O **Python c/ Cache** mantém latência estável e plana de **2,1 ms** independente da carga.
  - O **Python s/ Cache** sofre degradação progressiva, saltando de 16,5 ms para **109,2 ms** sob 200 usuários devido ao custo de parsing HTML.
  - O **Ruby** apresenta excelente comportamento a 10 usuários (4,7 ms c/ cache), mas a partir de 50 usuários a latência sobe para ~300 ms devido ao gargalo de fila.

---

## Slide 7: Vazão e Throughput (Requisições por Segundo)
- `[INSERIR IMAGEM: graficos/req_por_segundo.png]`
- **Destaques:**
  - **Escalabilidade Linear no Python:** A vazão escala de 9,8 req/s até atingir **200,8 req/s** com 200 usuários.
  - **Teto Fixo no Ruby:** O Ruby satura logo a 50 usuários em **~24,9 req/s**, mantendo-se estável nessa taxa em 100 e 200 usuários.

---

## Slide 8: Qualidade de Serviço e Percentil 95 (p95)
- `[INSERIR IMAGEM: graficos/percentil_95.png]`
- `[INSERIR IMAGEM: graficos/curva_percentis.png]`
- **Destaques:**
  - **Previsibilidade Extrema no Python com Cache:** O p95 manteve-se cravado em **3,0 ms**. 95% das requisições têm retorno imediato em memória.
  - **Degradação na Cauda Sem Cache:** No Python s/ Cache, o p95 atinge **520 ms** sob 200 usuários.
  - **Atraso de Fila no Ruby:** O p95 do Ruby atinge ~440–490 ms devido ao acúmulo no socket TCP.

---

## Slide 9: O Impacto Real do Cache Redis (Cálculo de Speedup)
- **Fórmula de Aceleração:**
  $$\text{Speedup} = \frac{\text{Tempo Sem Cache}}{\text{Tempo Com Cache}}$$
- **Resultados:**
  - Com **10 usuários:** $16,5\text{ ms} / 2,8\text{ ms} = \mathbf{5,9\times}$ mais rápido.
  - Com **200 usuários:** $109,2\text{ ms} / 2,1\text{ ms} = \mathbf{52,0\times}$ mais rápido.
- **Conclusão:** O benefício do cache cresce exponencialmente com o aumento da concorrência e do peso do payload das páginas.

---

## Slide 10: Análise Arquitetural: Gunicorn vs. Puma
- **Python / Gunicorn (Multi-worker prefork):**
  - Configuração: 4 processos workers e 2 threads por worker.
  - Distribuição real de trabalho entre múltiplos núcleos de CPU.
  - Excelente resposta a I/O e CPU-bound.
- **Ruby / Puma / Sinatra (Single-process):**
  - Execução em processo único sob o interpretador Ruby MRI (GVL - *Global VM Lock*).
  - Teto de processamento atingido em ~25 req/s.
  - **Lição de Engenharia:** Em sistemas distribuídos, a arquitetura do servidor de aplicação e o modelo de concorrência impactam o rendimento tanto ou mais do que a linguagem de programação.

---

## Slide 11: O Fenômeno do Cache Stampede (Thundering Herd)
- **O que observamos nos 50 usuários do Ruby:**
  - A largada simultânea de 50 usuários sobre um cache recém-limpo gerou 50 *Cache Misses* simultâneos para `page1.html`.
  - Todas as 50 conexões disputaram o mesmo processo Ruby para baixar o HTML, fazer parse no Nokogiri e gravar no Redis, elevando a média para 365,4 ms.
  - Em 100 e 200 usuários, com as chaves aquecidas, o cache voltou a superar o cenário sem cache (277 ms vs 312 ms e 294 ms vs 362 ms).
- **Soluções para Produção:**
  - *Cache Warming* (aquecimento prévio das rotas mais frequentes).
  - *Distributed Mutex / Lock* com Redis (`SET NX`).

---

## Slide 12: Conclusões e Considerações Finais
- **Eficácia Comprovada:** O Redis reduziu em até **98% o tempo de resposta** sob alta carga (**52× de speedup**).
- **Economia de Recursos:** Redução drástica de tráfego de rede e poupança de ciclos de CPU para re-parsing de DOM.
- **Estabilidade dos Testes:** 100% das requisições bem-sucedidas (0 falhas em 32.000+ chamadas) com calibragem realista de 10 a 200 usuários.
- **Próximos Passos:** Adição de balanceamento de carga (Nginx / HAProxy) e clusterização multi-processo no serviço Ruby.

