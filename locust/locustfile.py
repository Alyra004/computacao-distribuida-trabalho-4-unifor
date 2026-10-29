import os
from locust import HttpUser, SequentialTaskSet, task, between

# Lista com 10 URLs locais (servidas pelo container mock-target dentro da rede Docker)
MOCK_URLS = [
    f"http://mock-target/page{i}.html" for i in range(1, 11)
]

# Lista alternativa de 10 URLs reais na web
PUBLIC_URLS = [
    "http://example.com/",
    "http://example.org/",
    "http://example.net/",
    "http://info.cern.ch/",
    "http://neverssl.com/",
    "http://detectportal.firefox.com/success.txt",
    "http://captive.apple.com/",
    "http://msftconnecttest.com/connecttest.txt",
    "http://www.w3.org/History/1992/hypertext/hypermedia/Overview.html",
    "http://www.columbia.edu/~fdc/sample.html"
]

USE_MOCK = os.getenv("USE_MOCK_TARGET", "true").lower() in ("true", "1", "yes")
URL_LIST = MOCK_URLS if USE_MOCK else PUBLIC_URLS


class ExtractSequence(SequentialTaskSet):
    """
    Executa rigorosamente uma sequência de 10 invocações ao serviço de extração de link,
    passando uma URL diferente como parâmetro a cada invocação, conforme exigido no Trabalho 4.
    """

    @task
    def req_01(self):
        self._extract(0)

    @task
    def req_02(self):
        self._extract(1)

    @task
    def req_03(self):
        self._extract(2)

    @task
    def req_04(self):
        self._extract(3)

    @task
    def req_05(self):
        self._extract(4)

    @task
    def req_06(self):
        self._extract(5)

    @task
    def req_07(self):
        self._extract(6)

    @task
    def req_08(self):
        self._extract(7)

    @task
    def req_09(self):
        self._extract(8)

    @task
    def req_10(self):
        self._extract(9)

    def _extract(self, index: int):
        target_url = URL_LIST[index]
        endpoint = f"/api/{target_url}"
        # Nomeia agrupado para estatísticas gerais e individuais
        self.client.get(endpoint, name=f"extracao_url_{index+1:02d}")


class LinkExtractorUser(HttpUser):
    tasks = [ExtractSequence]
    # Intervalo de espera entre sequências de requisições de cada usuário
    wait_time = between(0.5, 1.5)
