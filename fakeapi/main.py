import fake
from fastapi import FastAPI

app = FastAPI()
cache = {}


@app.get("/cabecalho-processual/api/v1/processos/simples")
async def cabecalho_processual(cpfCnpj: str):
    cache_key = f"cabecalho_processual_{cpfCnpj}"
    if cache_key not in cache:
        cache[cache_key] = fake.cabecalho_processual(cpfCnpj)
    return cache[cache_key]


@app.get("/sisbajud/v1/relacionamento/{cpf_cnpj_entidade}")
async def sisbajud_contas(cpf_cnpj_entidade, cpfUsuarioSolicitante: str):
    cache_key = f"sisbajud_contas_{cpfUsuarioSolicitante}"
    if cache_key not in cache:
        cache[cache_key] = fake.sisbajud_contas(cpfUsuarioSolicitante)
    return cache[cache_key]


@app.get("/sisbajud/v1/ordem/")
async def sisbajud_ordens(codJuizDestinatario: str):
    cache_key = f"sisbajud_ordens_{codJuizDestinatario}"
    if cache_key not in cache:
        cache[cache_key] = fake.sisbajud_ordens(codJuizDestinatario)
    return cache[cache_key]


@app.get("/infojud/v1/requisicoes/dirpf/usuario/")
async def infojud_dirpf_ordens_lista():
    return fake.declaracao_renda_lista()


@app.get("/infojud/v1/requisicoes/efin/completa/usuario/")
async def infojud_efin_ordens_lista():
    return fake.declaracao_renda_lista()


@app.get("/infojud/v1/declaracao-renda/{cpf_cnpj_entidade}/{ano}")
async def infojud_ordens_detalhe(cpf_cnpj_entidade: str, ano: int):
    return fake.declaracao_renda_detalhe(cpf_cnpj_entidade, ano)


@app.get("/infojud/v1/declaracao-renda-pj/{cpf_cnpj_entidade}/{ano}")
async def infojud_ordens_detalhe_pj(cpf_cnpj_entidade: str, ano: int):
    return fake.declaracao_renda_detalhe_pj(cpf_cnpj_entidade, ano)
