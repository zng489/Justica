from urllib.parse import urljoin

import requests
from loguru import logger

from dataset.formatting import format_cnpj, format_cpf, format_numero_processo
from dataset.infojud_fields import (
    bens_fields,
    declaracao_lista_fields,
    declaracoes_fields,
    dependentes_fields,
    doacoes_pagamentos_fields,
    rendimentos_fields,
    resumo_fields,
)
from dataset.utils import uuid_from_document


class DeclaracaoRendaLista:
    fields = declaracao_lista_fields

    def __init__(self, api_url):
        self.api_url = api_url
        self.session = requests.Session()

    def get(self, url, token):
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.get(url, headers=headers)
        if response.ok:
            return response.json()
        else:
            logger.error(f"Error accessing endpoint {self.api_url}: {response.status_code} - {response.content}")
            return []

    def get_dirpf(self, token):
        url = urljoin(self.api_url, "v1/requisicoes/dirpf/usuario")
        return self.get(url, token)

    def get_efin(self, token):
        url = urljoin(self.api_url, "v1/requisicoes/efin/completa/usuario")
        return self.get(url, token)

    def parse_results(self, raw_result):
        parsed_results = []
        for result in raw_result:
            if len(result.get("documento")) == 14:
                result["documento"] = format_cnpj(result.get("documento"))
            else:
                result["documento"] = format_cpf(result.get("documento"))

            parsed_results.append(result)

        return parsed_results

    def execute(self, token):
        dirpf = self.parse_results(self.get_dirpf(token))
        efin = self.parse_results(self.get_efin(token))
        return dirpf + efin


class DeclaracaoRenda:
    fields = {
        "resumo": resumo_fields,
        "bens": bens_fields,
        "dependentes": dependentes_fields,
        "doacoes_pagamentos": doacoes_pagamentos_fields,
        "rendimentos": rendimentos_fields,
    }

    def __init__(self, api_url):
        self.api_url = api_url
        self.session = requests.Session()

    def get(self, cpf_cnpj_entidade, ano, token):
        url = urljoin(self.api_url, f"v1/declaracao-renda/{cpf_cnpj_entidade}/{ano}")
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.get(
            url,
            headers=headers,
        )
        if response.ok:
            return response.json()[0]
        else:
            logger.error(f"Error accessing endpoint {self.api_url}: {response.status_code} - {response.content}")
            return []

    def _parse_resumo(self, raw_result, declaracao):
        raw_resumo = declaracao[0].get("resumo", dict())
        resumo = {"ano": raw_result.get("ano")}
        resumo["documento"] = format_cpf(raw_result.get("cpfCnpj"))
        resumo["numero_processo"] = format_numero_processo(raw_result.get("numeroProcesso"))
        recepcao = raw_resumo.get("dataRecepcao", {})
        resumo["data_recepcao"] = f"{recepcao.get('dia')}/{recepcao.get('mes')}/{recepcao.get('ano')}"
        resumo["valor_imposto"] = raw_resumo.get("valorImposto")
        resumo["valor_base_calculo"] = raw_resumo.get("valorBaseCalculo")
        resumo["valor_rend_isentos"] = raw_resumo.get("valorRendIsentos")
        resumo["numero_dependentes"] = raw_resumo.get("numeroDependentes")
        fonte_principal = raw_resumo.get("numeroInscricaoFontePrincipal")
        if fonte_principal.get("isCpf"):
            codigo = format_cpf(fonte_principal.get("codigo"))
        else:
            codigo = format_cnpj(fonte_principal.get("codigo"))

        resumo["fonte_principal"] = codigo
        return {"fields": self.fields["resumo"], "result": resumo, "tab_name": "Resumo"}

    def _parse_bens(self, declaracao):
        rows = declaracao[0].get("bensDireitos", []) or []
        result = []
        for row in rows:
            result.append(
                {
                    "tipo": row.get("bemDireito"),
                    "valor_atual": row.get("valorAtual"),
                    "valor_anterior": row.get("valorAnterior"),
                    "descricao": row.get("descricaoBemParte1"),
                }
            )

        total = sum([r.get("valor_atual", 0) or 0 for r in result])
        total_anterior = sum([r.get("valor_anterior", 0) or 0 for r in result])

        return {
            "fields": self.fields["bens"],
            "result": result,
            "total": total,
            "total_anterior": total_anterior,
            "tab_name": "Bens e Direitos",
        }

    def _parse_dependentes(self, declaracao):
        rows = declaracao[0].get("dependentes", []) or []
        result = []
        for row in rows:
            documento = row.get("cpfDependente", {}).get("cpf", None) or None
            documento = str(documento or "").strip().replace(".", "").replace("-", "") if documento else None
            nascimento = row.get("dataNascimento", dict())
            data_nascimento = f"{nascimento.get('dia')}/{nascimento.get('mes')}/{nascimento.get('ano')}"
            new = {
                "nome": row.get("nomeDependente"),
                "documento": format_cpf(documento),
                "data_nascimento": data_nascimento,
                "tipo_dependente": row.get("tipoDependente"),
                "tipo_dependencia": row.get("tipoDependencia"),
            }
            _, new["object_uuid"] = uuid_from_document(documento)
            result.append(new)

        return {"fields": self.fields["dependentes"], "result": result, "tab_name": "Dependentes"}

    def _parse_doacoes_pagamentos(self, declaracao):
        rows = declaracao[0].get("doacoesPagamentos", []) or []
        result = []
        for row in rows:
            beneficiario = row.get("niBeneficiario", dict())
            if beneficiario.get("isCpf"):
                documento_beneficiario = format_cpf(beneficiario.get("codigo"))
            else:
                documento_beneficiario = format_cnpj(beneficiario.get("codigo"))

            result.append(
                {
                    "tipo_pagamento": row.get("tipoPagamento"),
                    "documento_beneficiario": documento_beneficiario,
                    "nome_beneficiario": row.get("nomeBeneficiario"),
                    "doacao_pagamento": row.get("doacaoPagamento"),
                    "nome_dependente": row.get("nomeDependente"),
                    "valor": row.get("valorDoacaoPagamento"),
                }
            )

        total = sum(r.get("valor", 0) or 0 for r in result)

        return {
            "fields": self.fields["doacoes_pagamentos"],
            "result": result,
            "total": total,
            "tab_name": "Doações e Pagamentos",
        }

    def _sum_valor(self, row):
        return sum(row.get(key, 0) or 0 for key in row.keys() if key.startswith("valor"))

    def _parse_rendimentos_pj(self, rendimentos):
        rows = rendimentos.get("rendimentosPJ", []) or []
        tipo_rendimento = "Rendimentos PJ"
        results = []
        for row in rows:
            results.append(
                {
                    "tipo_rendimento": tipo_rendimento,
                    "nome_fonte_pagadora": row.get("nomeFontePagadora"),
                    "documento_fonte_pagadora": format_cnpj(row.get("cnpjFontePagadora")),
                    "cpf_beneficiario": format_cpf(row.get("cpfBeneficiario")),
                    "descricao": None,
                    "valor": self._sum_valor(row),
                }
            )

        return results

    def _parse_rendimentos_isentos_nt(self, rendimentos):
        return {
            "tipo_rendimento": "Rendimentos isentos não tributáveis",
            "nome_fonte_pagadora": None,
            "documento_fonte_pagadora": None,
            "cpf_beneficiario": None,
            "descricao": None,
            "valor": self._sum_valor(rendimentos.get("rendimentosIsentosNT")),
        }

    def _parse_rendimentos_isentos(self, rendimentos):
        rows = rendimentos.get("rendimentosIsentosDetalhes", []) or []
        tipo_rendimento = "Rendimentos isentos"
        results = []
        for row in rows:
            fonte_pagdora = row.get("fontePagadora")
            if fonte_pagdora.get("isCpf"):
                documento = format_cpf(fonte_pagdora.get("codigo"))
            else:
                documento = format_cnpj(fonte_pagdora.get("codigo"))
            results.append(
                {
                    "tipo_rendimento": tipo_rendimento,
                    "nome_fonte_pagadora": row.get("nomeFontePagadora"),
                    "documento_fonte_pagadora": documento,
                    "cpf_beneficiario": format_cpf(row.get("cpfBeneficiario")),
                    "descricao": row.get("descricaoRendimento"),
                    "valor": self._sum_valor(row),
                },
            )

        return results

    def _parse_rendimentos_acumulados(self, rendimentos):
        rows = rendimentos.get("rendimentosRecebidosAcumuladamente", []) or []
        tipo_rendimento = "Rendimentos recebidos acumuladamente"
        results = []
        for row in rows:
            fonte_pagdora = row.get("niFontePagadora")
            if fonte_pagdora.get("isCpf"):
                documento = format_cpf(fonte_pagdora.get("codigo"))
            else:
                documento = format_cnpj(fonte_pagdora.get("codigo"))
            results.append(
                {
                    "tipo_rendimento": tipo_rendimento,
                    "nome_fonte_pagadora": row.get("nomeFontePagadora"),
                    "documento_fonte_pagadora": documento,
                    "cpf_beneficiario": None,
                    "descricao": None,
                    "valor": self._sum_valor(row),
                }
            )

        return results

    def _parse_rendimentos_tributacao_exclusiva(self, rendimentos):
        return {
            "tipo_rendimento": "Rendimentos com tributação exclusiva na fonte",
            "nome_fonte_pagadora": None,
            "documento_fonte_pagadora": None,
            "cpf_beneficiario": None,
            "descricao": None,
            "valor": self._sum_valor(rendimentos.get("rendimentosTributacaoExclusivaFonte")),
        }

    def _parse_rendimentos_tributacao_exclusiva_detalhe(self, rendimentos):
        rows = rendimentos.get("rendimentosTributacaoExclusivaFonteDetalhes", []) or []
        tipo_rendimento = "Rendimentos com tributação exclusiva na fonte"
        results = []
        for row in rows:
            fonte_pagdora = row.get("niFontePagadora")
            if fonte_pagdora.get("isCpf"):
                documento = format_cpf(fonte_pagdora.get("codigo"))
            else:
                documento = format_cnpj(fonte_pagdora.get("codigo"))
            results.append(
                {
                    "tipo_rendimento": tipo_rendimento,
                    "nome_fonte_pagadora": row.get("nomeFontePagadora"),
                    "documento_fonte_pagadora": documento,
                    "cpf_beneficiario": format_cpf(row.get("cpfBeneficiario")),
                    "descricao": None,
                    "valor": row.get("valorRecebimento"),
                }
            )

        return results

    def _parse_rendimentos(self, declaracao):
        rendimentos = declaracao[0].get("rendimentos", dict()) or dict()
        result = self._parse_rendimentos_pj(rendimentos)
        result.append(self._parse_rendimentos_isentos_nt(rendimentos))
        result.extend(self._parse_rendimentos_isentos(rendimentos))
        result.extend(self._parse_rendimentos_acumulados(rendimentos))
        result.append(self._parse_rendimentos_tributacao_exclusiva(rendimentos))
        result.extend(self._parse_rendimentos_tributacao_exclusiva_detalhe(rendimentos))
        total = sum(r.get("valor", 0) or 0 for r in result)
        return {
            "fields": self.fields["rendimentos"],
            "result": result,
            "total": total,
            "tab_name": "Rendimentos",
        }

    def parse_results(self, raw_result):
        declaracao = raw_result.get("dirpf")
        result = {"resumo": self._parse_resumo(raw_result, declaracao)}
        result["bens"] = self._parse_bens(declaracao)
        result["dependentes"] = self._parse_dependentes(declaracao)
        result["doacoes_pagamentos"] = self._parse_doacoes_pagamentos(declaracao)
        result["rendimentos"] = self._parse_rendimentos(declaracao)
        return result

    def execute(self, token, cpf_cnpj_entidade, ano):
        # https://gateway.stg.cloud.pje.jus.br/infojud/swagger-ui.html#/
        # TODO: pegar documento enviado pelo usuário
        # TODO: fazer requisição para API de DIRPF ou DIRPJ, de acordo com o
        return self.parse_results(self.get(cpf_cnpj_entidade, ano, token))


class DeclaracaoRendaPJ:
    fields = {
        "declaracoes": declaracoes_fields,
    }

    def __init__(self, api_url):
        self.api_url = api_url
        self.session = requests.Session()

    def get(self, cpf_cnpj_entidade, ano, token):
        url = urljoin(self.api_url, f"v1/declaracao-renda-pj/{cpf_cnpj_entidade}/{ano}")
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.get(
            url,
            headers=headers,
        )
        if response.ok:
            return response.json()[0]
        else:
            logger.error(f"Error accessing endpoint {self.api_url}: {response.status_code} - {response.content}")
            return []

    def _parse_declaracoes(self, declaracoes):
        result = []
        for row in declaracoes:
            info_declarado = row.get("informacaoesBasicasDeclarado", [dict()])
            for info in info_declarado:
                conta_declarado = info.get("contaDeclarado", []) or []
                n_contas = min(2, len(conta_declarado))
                for conta in conta_declarado[:n_contas]:
                    result.append(
                        {
                            "nome_declarante": row.get("nomeDeclarante"),
                            "cnpj_declarante": format_cnpj(row.get("cnpjDeclarante")),
                            "ano": row.get("anoDeclaracao"),
                            "nome_declarado": info.get("nomeDeclarado"),
                            "id_declarado": row.get("niDeclarado"),
                            "conta_declarado": conta.get("numeroConta"),
                            "relacao_declarado": conta.get("relacaoDeclarado"),
                            "tipo_conta_declarado": conta.get("tipoContaDescricao"),
                            "total_debitos": conta.get("valores", dict()).get("totDebitos"),
                            "total_creditos": conta.get("valores", dict()).get("totCreditos"),
                            "pais_declarado": info.get("paisEnderecoDescricaoDeclarado"),
                        }
                    )

        return {
            "fields": declaracoes_fields,
            "result": result,
            "tab_name": "Declarações",
        }

    def parse_results(self, raw_result):
        declaracoes = raw_result["eFinanceira"][0]["declaracao"]
        result = {"declaracoes": self._parse_declaracoes(declaracoes)}
        return result

    def execute(self, token, cpf_cnpj_entidade, ano):
        # TODO: pegar documento enviado pelo usuário
        # TODO: fazer requisição para API de DIRPF ou DIRPJ, de acordo com o
        return self.parse_results(self.get(cpf_cnpj_entidade, ano, token))
