resumo_fields = [
    {
        "name": "ano",
        "title": "Ano",
        "type": "int",
        "description": "Ano da declaração",
    },
    {
        "name": "documento",
        "title": "Documento",
        "type": "string",
        "description": "Documento de identificação",
    },
    {
        "name": "fonte_principal",
        "title": "Fonte principal",
        "type": "string",
        "description": "Fonte principal",
    },
    {
        "name": "numero_processo",
        "title": "Número do processo",
        "type": "string",
        "description": "Número do processo",
    },
    {
        "name": "data_recepcao",
        "title": "Data da recepção",
        "type": "date",
        "description": "Data da recepção da declaração",
    },
    {
        "name": "valor_imposto",
        "title": "Valor do imposto",
        "type": "numeric",
        "description": "Valor do imposto",
    },
    {
        "name": "valor_base_calculo",
        "title": "Valor base cálculo",
        "type": "numeric",
        "description": "Valor base cálculo",
    },
    {
        "name": "valor_rend_isentos",
        "title": "Valor de rendimentos isentos",
        "type": "numeric",
        "description": "Valor de rendimentos isentos",
    },
    {
        "name": "numero_dependentes",
        "title": "Número de dependentes",
        "type": "int",
        "description": "Número de dependentes",
    },
]


bens_fields = [
    {
        "name": "tipo",
        "title": "Tipo",
        "type": "string",
        "description": "Tipo de bem ou direito",
    },
    {
        "name": "valor_atual",
        "title": "Valor atual",
        "type": "numeric(15, 2)",
        "description": "Valor atual",
    },
    {
        "name": "valor_anterior",
        "title": "Valor anterior",
        "type": "numeric(15, 2)",
        "description": "Valor anterior",
    },
    {
        "name": "descricao",
        "title": "Descrição",
        "type": "string",
        "description": "Descrição",
    },
]


declaracao_lista_fields = [
    {
        "name": "nome",
        "title": "Nome",
        "type": "string",
        "description": "Nome",
    },
    {
        "name": "documento",
        "title": "Documento",
        "type": "string",
        "description": "Número do documento",
    },
    {
        "name": "numero_processo",
        "title": "Número do processo",
        "type": "string",
        "description": "Número do processo",
    },
]


dependentes_fields = [
    {
        "name": "nome",
        "title": "Nome",
        "type": "string",
        "description": "Nome",
    },
    {
        "name": "documento",
        "title": "Documento",
        "type": "string",
        "description": "Documento",
    },
    {
        "name": "data_nascimento",
        "title": "Data de nascimento",
        "type": "date",
        "description": "Data de nascimento",
    },
    {
        "name": "tipo_dependente",
        "title": "Tipo de dependente",
        "type": "string",
        "description": "Tipo de dependente",
    },
    {
        "name": "tipo_dependencia",
        "title": "Tipo de dependencia",
        "type": "string",
        "description": "Tipo de dependencia",
    },
    {
        "name": "object_uuid",
        "title": "object_uuid",
        "type": "string",
        "description": "object_uuid",
        "show": False,
    },
]


doacoes_pagamentos_fields = [
    {
        "name": "tipo_pagamento",
        "title": "Tipo de pagamento",
        "type": "string",
        "description": "Tipo de pagamento",
    },
    {
        "name": "documento_beneficiario",
        "title": "Documento do beneficiário",
        "type": "string",
        "description": "Documento do beneficiário",
    },
    {
        "name": "nome_beneficiario",
        "title": "Nome do beneficiário",
        "type": "string",
        "description": "Nome do beneficiário",
    },
    {
        "name": "doacao_pagamento",
        "title": "Pagamento",
        "type": "string",
        "description": "Pagamento",
    },
    {
        "name": "nome_dependente",
        "title": "Nome do dependente",
        "type": "string",
        "description": "Nome do dependente",
    },
    {
        "name": "valor",
        "title": "Valor",
        "type": "numeric",
        "description": "Valor",
    },
]


rendimentos_fields = [
    {"name": "tipo_rendimento", "title": "Tipo de rendimento", "type": "string", "description": "Tipo de rendimento"},
    {
        "name": "nome_fonte_pagadora",
        "title": "Nome da fonte pagadora",
        "type": "string",
        "description": "Nome da fonte pagadora",
    },
    {
        "name": "documento_fonte_pagadora",
        "title": "Documento da fonte pagadora",
        "type": "string",
        "description": "Documento da fonte pagadora",
    },
    {
        "name": "cpf_beneficiario",
        "title": "CPF do beneficiário",
        "type": "string",
        "description": "CPF do beneficiário",
    },
    {
        "name": "descricao",
        "title": "Descrição",
        "type": "string",
        "description": "Descrição",
    },
    {
        "name": "valor",
        "title": "Valor",
        "type": "numeric",
        "description": "Valor",
    },
]


declaracoes_fields = [
    {"name": "nome_declarante", "title": "Nome do declarante", "type": "string", "description": "Nome do declarante"},
    {"name": "cnpj_declarante", "title": "CNPJ do declarante", "type": "string", "description": "CNPJ do declarante"},
    {
        "name": "ano",
        "title": "Ano da declaração",
        "type": "string",
        "description": "Ano da declaração",
    },
    {
        "name": "nome_declarado",
        "title": "Nome do declarado",
        "type": "string",
        "description": "Nome do declarado",
    },
    {
        "name": "id_declarado",
        "title": "Identificação do declarado",
        "type": "string",
        "description": "Identificação do declarado",
    },
    {
        "name": "conta_declarado",
        "title": "Número da conta bancária",
        "type": "string",
        "description": "Número da conta bancária",
    },
    {
        "name": "relacao_declarado",
        "title": "Relação com a conta",
        "type": "string",
        "description": "Relação com a conta bancária",
    },
    {
        "name": "tipo_conta_declarado",
        "title": "Tipo de conta",
        "type": "string",
        "description": "Tipo de conta bancária",
    },
    {
        "name": "total_debitos",
        "title": "Total de débitos",
        "type": "numeric",
        "description": "Total de débitos",
    },
    {
        "name": "total_creditos",
        "title": "Total de créditos",
        "type": "numeric",
        "description": "Total de créditos",
    },
]
