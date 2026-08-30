# VPS Metrics API

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Google Analytics](https://img.shields.io/badge/Google%20Analytics-4-E37400?logo=googleanalytics&logoColor=white)](https://developers.google.com/analytics/devguides/reporting/data/v1)
[![Pytest](https://img.shields.io/badge/Tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org/)

API somente leitura para métricas do host, containers Docker e relatórios Google Analytics 4.

## Configuração

1. Copie `.env.example` para `.env`, ou configure as mesmas variáveis diretamente no EasyPanel/ambiente do servidor.
2. Substitua `API_TOKEN=change-me` por um token forte.
3. Substitua `PRIVATE_PORTAL_PASSWORD=change-me-too` por uma senha forte.
4. Defina `DOCS_HOST` com o hostname que deve abrir o Swagger diretamente, por exemplo `docs.example.com`.
5. Defina `TIMEZONE=America/Sao_Paulo` ou outro fuso IANA para os timestamps da API.
6. Defina `GA_PROPERTY_ID` com o ID numérico da propriedade GA4.
7. Monte uma chave de service account em `secrets/google-service-account.json` e dê a ela o papel Viewer na propriedade GA4.
8. Execute `docker compose up -d --build`.

`API_TOKEN` e `PRIVATE_PORTAL_PASSWORD` são obrigatórios. Apenas `PORT=8000` não configura essas credenciais.

O socket Docker é montado somente para leitura. Não exponha a porta 2375 nem a porta desta API sem HTTPS e autenticação.

## Endpoints

- `GET /api/v1/health` não exige autenticação.
- `GET /api/v1/metrics/system` retorna CPU, memória, disco, uptime e contadores de rede.
- `GET /api/v1/metrics/docker` retorna estado, health, reinícios, portas e uso dos containers.
- `GET /api/v1/metrics/analytics?start_date=2026-01-01&end_date=2026-01-31` retorna totais GA4, origens e páginas.

As rotas protegidas exigem `Authorization: Bearer <API_TOKEN>`. A documentação interativa fica em `/docs`.

Para integrações rápidas, também existem aliases curtos: `/health`, `/system`, `/docker` e `/analytics`. Eles mantêm a mesma autenticação e resposta das rotas versionadas.

## Portais

- Portal público: `/`, contendo somente o estado operacional básico.
- Portal privado: `/private`, protegido por `PRIVATE_PORTAL_USER` e `PRIVATE_PORTAL_PASSWORD`.
- Swagger privado: `/private/docs`, com schema em `/private/openapi.json`.

Quando `DOCS_HOST` estiver configurado, o Swagger também abrirá diretamente na raiz desse domínio.

O portal privado usa autenticação HTTP Basic. As chamadas de métricas dentro do Swagger continuam exigindo `Authorization: Bearer <API_TOKEN>`.

## Desenvolvimento

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn src.main:app --reload
```

---

## English Documentation

Read-only API for host metrics, Docker containers, and Google Analytics 4 reports.

### Configuration

1. Copy `.env.example` to `.env`, or configure the same variables directly in EasyPanel/server environment settings.
2. Replace `API_TOKEN=change-me` with a strong token.
3. Replace `PRIVATE_PORTAL_PASSWORD=change-me-too` with a strong password.
4. Set `DOCS_HOST` to the hostname that should open Swagger directly, for example `docs.example.com`.
5. Set `TIMEZONE=America/Sao_Paulo` or another IANA timezone for API timestamps.
6. Set `GA_PROPERTY_ID` to the numeric GA4 property ID.
7. Mount a service account key at `secrets/google-service-account.json` and grant it the Viewer role on the GA4 property.
8. Run `docker compose up -d --build`.

`API_TOKEN` and `PRIVATE_PORTAL_PASSWORD` are required. The Docker socket is mounted read-only. Do not expose port 2375 or this API without HTTPS and authentication.

### Endpoints

- `GET /api/v1/health` is public.
- `GET /api/v1/metrics/system` returns CPU, memory, disk, uptime, and network counters.
- `GET /api/v1/metrics/docker` returns container state, health, restarts, ports, and resource usage.
- `GET /api/v1/metrics/analytics?start_date=2026-01-01&end_date=2026-01-31` returns GA4 totals, sources, and pages.

Short aliases are also available: `/health`, `/system`, `/docker`, and `/analytics`. Protected routes require `Authorization: Bearer <API_TOKEN>`.

### Portals

- Public portal: `/`, with basic operational status.
- Private portal: `/private`, protected by `PRIVATE_PORTAL_USER` and `PRIVATE_PORTAL_PASSWORD`.
- Private Swagger: `/private/docs`, with its schema at `/private/openapi.json`.

When `DOCS_HOST` is configured, Swagger also opens directly at the root of that hostname. The private portal uses HTTP Basic authentication, while metric requests from Swagger still require the Bearer token.

### Development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn src.main:app --reload
```