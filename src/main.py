from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasicCredentials

from src.auth import basic, require_private_portal, require_token, validate_private_credentials
from src.collectors.analytics import collect_analytics_metrics
from src.collectors.docker import collect_docker_metrics
from src.collectors.system import collect_system_metrics
from src.config import Settings, get_settings
from src.models.metrics import AnalyticsMetrics, DockerMetrics, HealthResponse, SystemMetrics

app = FastAPI(title="VPS Metrics API", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)
settings = get_settings()
if settings.allowed_origins:
    app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_methods=["GET"], allow_headers=["Authorization", "Content-Type"])


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def public_portal(request: Request, credentials: Annotated[HTTPBasicCredentials | None, Depends(basic)], config: Annotated[Settings, Depends(get_settings)]) -> HTMLResponse:
    if config.docs_host and request.url.hostname == config.docs_host:
        validate_private_credentials(credentials, config)
        return get_swagger_ui_html(openapi_url="/private/openapi.json", title="VPS Metrics API - Swagger")
    return HTMLResponse(content="""<!doctype html>
<html lang='pt-BR'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>
<title>VPS Metrics | Operações</title><style>
:root{color-scheme:dark;--bg:#0b1118;--panel:#121c27;--panel2:#172532;--line:#263746;--text:#edf5f7;--muted:#9db0b8;--accent:#43d6b2;--blue:#77bdfb}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(circle at 80% 0%,#17333b 0,#0b1118 42%);color:var(--text);font:16px/1.5 ui-sans-serif,system-ui,sans-serif}
main{width:min(100% - 40px,960px);margin:0 auto;padding:72px 0 56px}.brand{display:flex;align-items:center;gap:13px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;font-size:12px;font-weight:700}.mark{width:36px;height:36px;border:2px solid var(--accent);border-radius:11px;display:grid;place-items:center;color:var(--accent);font-size:18px}.hero{display:flex;justify-content:space-between;gap:32px;align-items:end;margin:52px 0 34px}.hero h1{font-size:clamp(38px,7vw,72px);line-height:1.02;letter-spacing:-.04em;margin:0 0 16px}.hero p{color:var(--muted);font-size:18px;margin:0;max-width:520px}.pill{white-space:nowrap;border:1px solid #2d665e;background:#12352f;color:var(--accent);border-radius:999px;padding:8px 13px;font-size:13px;font-weight:700}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.card{background:linear-gradient(145deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:8px;padding:22px;min-height:150px}.card small{display:block;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:11px;font-weight:700;margin-bottom:18px}.card strong{font-size:22px}.card p{color:var(--muted);margin:8px 0 0;font-size:14px}.links{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}.link{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:6px;padding:12px 16px;color:var(--text);text-decoration:none;background:#101a24}.link.primary{background:var(--accent);border-color:var(--accent);color:#08231e;font-weight:800}.link:hover{border-color:var(--blue)}footer{margin-top:62px;color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:18px}@media(max-width:650px){main{padding-top:38px;width:min(100% - 28px,960px)}.hero{display:block;margin-top:42px}.pill{display:inline-block;margin-top:22px}.grid{grid-template-columns:1fr}.card{min-height:0}}
</style></head><body><main><div class='brand'><span class='mark'>⌁</span> VPS Metrics <span>·</span> Operations</div>
<section class='hero'><div><h1>Visibilidade<br>do seu servidor.</h1><p>Um ponto de acesso simples para acompanhar a saúde da infraestrutura, os serviços Docker e os dados do seu website.</p></div><span class='pill'>● Sistema operacional</span></section>
<section class='grid'><article class='card'><small>Disponibilidade</small><strong>Online</strong><p>API respondendo normalmente.</p></article><article class='card'><small>Infraestrutura</small><strong>CPU · Memória · Disco</strong><p>Métricas do host disponíveis no portal privado.</p></article><article class='card'><small>Website</small><strong>Google Analytics 4</strong><p>Relatórios de tráfego e comportamento.</p></article></section>
<nav class='links'><a class='link primary' href='/private/docs'>Abrir Swagger <span>→</span></a><a class='link' href='/api/v1/health'>Verificar disponibilidade <span>↗</span></a><a class='link' href='/private'>Portal privado <span>→</span></a></nav>
<footer>Última verificação disponível em <a href='/health' style='color:var(--blue)'>/health</a></footer></main></body></html>""")


@app.get("/private", response_class=HTMLResponse, dependencies=[Depends(require_private_portal)], include_in_schema=False)
def private_portal() -> str:
    return """<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>VPS Metrics Private</title></head><body><main><h1>Portal privado</h1><p>Acesso operacional autorizado.</p><p><a href='/private/docs'>Abrir Swagger UI</a></p><p><a href='/api/v1/metrics/system'>Métricas do sistema</a></p><p><a href='/api/v1/metrics/docker'>Métricas Docker</a></p><p><a href='/api/v1/metrics/analytics'>Google Analytics</a></p></main></body></html>"""


@app.get("/private/openapi.json", dependencies=[Depends(require_private_portal)], include_in_schema=False)
def private_openapi() -> JSONResponse:
    return JSONResponse(app.openapi())


@app.get("/private/docs", response_class=HTMLResponse, dependencies=[Depends(require_private_portal)], include_in_schema=False)
def private_docs() -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="/private/openapi.json", title="VPS Metrics API - Swagger")


@app.get("/health", response_model=HealthResponse, include_in_schema=False)
@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=get_settings().now())


@app.get("/system", response_model=SystemMetrics, dependencies=[Depends(require_token)], include_in_schema=False)
@app.get("/api/v1/metrics/system", response_model=SystemMetrics, dependencies=[Depends(require_token)])
def system_metrics(config: Annotated[Settings, Depends(get_settings)]) -> SystemMetrics:
    return collect_system_metrics(config.disk_path)


@app.get("/docker", response_model=DockerMetrics, dependencies=[Depends(require_token)], include_in_schema=False)
@app.get("/api/v1/metrics/docker", response_model=DockerMetrics, dependencies=[Depends(require_token)])
def docker_metrics(config: Annotated[Settings, Depends(get_settings)]) -> DockerMetrics:
    return collect_docker_metrics(config.docker_host)


@app.get("/analytics", response_model=AnalyticsMetrics, dependencies=[Depends(require_token)], include_in_schema=False)
@app.get("/api/v1/metrics/analytics", response_model=AnalyticsMetrics, dependencies=[Depends(require_token)])
def analytics_metrics(
    config: Annotated[Settings, Depends(get_settings)],
    start_date: date = Query(default_factory=lambda: date.today().replace(day=1)),
    end_date: date = Query(default_factory=date.today),
) -> AnalyticsMetrics:
    if start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date deve ser anterior a end_date")
    if not config.ga_property_id:
        raise HTTPException(status_code=503, detail="GA_PROPERTY_ID nao configurado")
    return collect_analytics_metrics(config.ga_property_id, start_date.isoformat(), end_date.isoformat())