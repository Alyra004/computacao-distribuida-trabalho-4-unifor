# Projeto 3 – Testes de Carga com Múltiplas Instâncias do WordPress Utilizando o Locust

Trabalho 3 da disciplina de Computação Distribuída (UNIFOR): realizar testes de carga com o **Locust** nas múltiplas instâncias do WordPress do Trabalho 2 (Nginx como balanceador de carga e Docker Compose), variando o número de instâncias e o número de usuários simultâneos.

## Equipe

| Nome | Matrícula |
|---|---|
| João Igor Vidal de Andrade | 2320296 |
| Raquel Albuquerque Quirino | 2320325 |
| Amanda Lira Andrade Botelho | 2320291 |

## Sobre o projeto

Teste de carga é a prática de simular vários usuários acessando um software ao mesmo tempo para medir o desempenho percebido pelo usuário final. Aqui o **Locust** gera a carga sobre três cenários de blog post (imagem de ~1 MB, texto de ~400 KB e imagem de ~300 KB), com 10, 100 e 1000 usuários simultâneos e com 1, 2 e 3 instâncias do WordPress: **27 execuções** no total. Os resultados são apresentados em gráficos, com usuários ou instâncias no eixo X e as métricas do Locust no eixo Y.

