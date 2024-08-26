WITH to_update AS (
  SELECT DISTINCT id_entidade AS cnpj_raiz
  FROM eventos_atualizacao
  WHERE
    dt_evento BETWEEN '{{ start_datetime }}' AND '{{ end_datetime }}'
    AND nm_entidade IN ('estabelecimento', 'empresa', 'simples')
),
estabelecimento_norm AS (
  SELECT
    nu_cnpj_raiz AS cnpj_raiz,
    nu_cnpj_raiz || id_estabelecimento AS cnpj,
    text_or_null(te_dados->>'nomeFantasia') AS nome_fantasia,
    (
      ARRAY[te_dados->>'cnaeFiscal']
      || (
        CASE
          WHEN te_dados->>'cnaesSecundarias' <> '' THEN ARRAY(SELECT jsonb_array_elements_text((te_dados->>'cnaesSecundarias')::jsonb))
          ELSE ARRAY[]::text[]
        END
      )
    ) AS cnae,
    parse_date(te_dados->>'dataCadastro') AS data_cadastro,
    parse_date(te_dados->>'dataSituacaoCadastral') AS data_situacao_cadastral,
    (te_dados->>'situacaoCadastral')::smallint AS codigo_situacao_cadastral,
    (te_dados->>'motivoSituacaoCadastral')::smallint AS codigo_motivo_situacao_cadastral,
    CASE
        WHEN
          COALESCE(te_dados->>'dataSituacaoEspecial', '') <> ''
          AND COALESCE(te_dados->>'situacaoEspecial', '') <> ''
        THEN parse_date(te_dados->>'dataSituacaoEspecial')
        ELSE NULL
    END AS data_situacao_especial,
    text_or_null(te_dados->>'situacaoEspecial') AS situacao_especial,
    text_or_null(te_dados->>'tipoLogradouro') AS tipo_logradouro,
    text_or_null(te_dados->>'logradouro') AS logradouro,
    text_or_null(te_dados->>'numero') AS numero_logradouro,
    text_or_null(te_dados->>'complemento') AS complemento,
    text_or_null(te_dados->>'bairro') AS bairro,
    text_or_null(te_dados->>'municipio')::smallint AS codigo_municipio,
    text_or_null(te_dados->>'uf') AS uf,
    text_or_null(te_dados->>'cep') AS cep,
    text_or_null(te_dados->>'cidadeExterior') AS cidade_exterior,
    text_or_null(te_dados->>'pais')::smallint AS codigo_pais,
    text_or_null(te_dados->>'ddd1') AS ddd_1,
    remove_zero(te_dados->>'telefone1') AS telefone_1,
    text_or_null(te_dados->>'ddd2') AS ddd_2,
    remove_zero(te_dados->>'telefone2') AS telefone_2,
    text_or_null(te_dados->>'email') AS email
  FROM estabelecimentos AS e
  WHERE
    te_dados->>'identificadorMatrizFilial' = '1'
    AND nu_cnpj_raiz IN (SELECT cnpj_raiz FROM to_update)
),
empresa_norm AS (
 SELECT
   nu_cnpj_raiz AS cnpj_raiz,
   ROUND((te_dados->>'capitalSocial')::decimal / 100, 2) AS capital_social,
   text_or_null(te_dados->>'qualificacaoResponsavel')::smallint AS codigo_qualificacao_responsavel,
   te_dados->>'nomeEmpresarial' AS razao_social,
   text_or_null(te_dados->>'naturezaJuridica')::smallint AS codigo_natureza_juridica,
   text_or_null(te_dados->>'porteEmpresa')::smallint AS codigo_porte,
   text_or_null(te_dados->>'cpfResponsavel') AS cpf_responsavel
 FROM empresas
 WHERE nu_cnpj_raiz IN (SELECT cnpj_raiz FROM to_update)
),
simples_norm AS (
  SELECT nu_cnpj_raiz AS cnpj_raiz
  FROM simples
  WHERE
    te_dados @> '{"simples": [{"dataFim": "00000000"}]}'::jsonb
    AND nu_cnpj_raiz IN (SELECT cnpj_raiz FROM to_update)
),
mei_norm AS (
  SELECT nu_cnpj_raiz AS cnpj_raiz
  FROM simples
  WHERE
    te_dados @> '{"mei": [{"dataFim": "00000000"}]}'::jsonb
    AND nu_cnpj_raiz IN (SELECT cnpj_raiz FROM to_update)
)
SELECT
  company_uuid(e.cnpj_raiz) AS object_uuid,
  NOW() AS updated_at,
  e.cnpj,
  c.razao_social,
  e.nome_fantasia,
  e.cnae,
  e.data_cadastro,
  e.data_situacao_cadastral,
  e.codigo_situacao_cadastral,
  e.codigo_motivo_situacao_cadastral,
  e.data_situacao_especial,
  e.situacao_especial,
  TRIM(
   COALESCE(e.tipo_logradouro, '') || ' '
   || COALESCE(e.logradouro, '') || ', '
   || COALESCE(e.numero_logradouro, '')
   || CASE WHEN e.complemento IS NOT NULL THEN ' (' || e.complemento || ')' ELSE '' END
   || ' - ' || COALESCE(e.bairro, '')
  ) AS endereco,
  e.codigo_municipio,
  e.uf,
  e.cep,
  e.cidade_exterior,
  e.codigo_pais,
  TRIM(COALESCE(e.ddd_1, '') || ' ' || COALESCE(e.telefone_1, '')) AS telefone_1,
  TRIM(COALESCE(e.ddd_2, '') || ' ' || COALESCE(e.telefone_2, '')) AS telefone_2,
  e.email,
  c.capital_social,
  c.codigo_qualificacao_responsavel,
  c.codigo_natureza_juridica,
  c.codigo_porte,
  c.cpf_responsavel,
  CASE
    WHEN s.cnpj_raiz IS NOT NULL THEN TRUE
    ELSE FALSE
  END AS opcao_simples,
  CASE
    WHEN m.cnpj_raiz IS NOT NULL THEN TRUE
    ELSE FALSE
  END AS opcao_mei
  FROM estabelecimento_norm AS e
    LEFT JOIN empresa_norm AS c
      ON e.cnpj_raiz = c.cnpj_raiz
    LEFT JOIN simples_norm AS s
      ON e.cnpj_raiz = s.cnpj_raiz
    LEFT JOIN mei_norm AS m
      ON e.cnpj_raiz = m.cnpj_raiz
