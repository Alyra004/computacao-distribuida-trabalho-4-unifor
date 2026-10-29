#!/usr/bin/env python
import os
import json
import logging
from flask import Flask, request, jsonify, Response
import redis
from linkextractor import extract_links

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() in ("true", "1", "yes")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

redis_conn = None
if ENABLE_CACHE:
    try:
        redis_conn = redis.from_url(REDIS_URL)
        logger.info(f"[Python API] Redis cache ativado em {REDIS_URL}")
    except Exception as e:
        logger.warning(f"[Python API] Falha ao inicializar conexão com Redis: {e}. Executando sem cache.")
else:
    logger.info("[Python API] Executando em modo SEM CACHE (ENABLE_CACHE=false)")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "api-python", "cache": ENABLE_CACHE})

@app.route("/")
def index():
    return "Usage: http://<hostname>[:<port>]/api/<url>"

@app.route("/api/<path:url>")
def api(url):
    qs = request.query_string.decode("utf-8")
    if qs != "":
        url += "?" + qs

    # 1. Verifica cache se habilitado
    if ENABLE_CACHE and redis_conn is not None:
        try:
            cached = redis_conn.get(url)
            if cached:
                logger.debug(f"[CACHE HIT] {url}")
                return Response(cached, status=200, mimetype="application/json")
        except Exception as e:
            logger.warning(f"[REDIS ERROR] {e}")

    # 2. Extrai da URL
    logger.debug(f"[CACHE MISS/NO-CACHE] Extraindo {url}")
    links = extract_links(url)
    jsonlinks = json.dumps(links, indent=2)

    # 3. Armazena em cache se habilitado
    if ENABLE_CACHE and redis_conn is not None:
        try:
            redis_conn.set(url, jsonlinks)
        except Exception as e:
            logger.warning(f"[REDIS SET ERROR] {e}")

    return Response(jsonlinks, status=200, mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
