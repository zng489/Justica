WITH mei_norm AS (
  SELECT nu_cnpj_raiz AS cnpj_raiz
  FROM simples
  WHERE te_dados @> '{"mei": [{"dataFim": "00000000"}]}'::jsonb
)
SELECT
  CASE
    WHEN t.codigo_tipo_socio = 1 THEN company_uuid(t.documento)
    WHEN t.codigo_tipo_socio = 2 THEN person_uuid(t.documento)
    ELSE NULL
  END AS from_node_uuid,
  company_uuid(t.cnpj_raiz) AS to_node_uuid,
  'is_partner' AS relationship,
  json_build_object(
    'codigo_qualificacao', t.codigo_qualificacao,
    'data_entrada_sociedade', t.data_entrada_sociedade,
    'codigo_pais', t.codigo_pais,
    'codigo_tipo_socio', t.codigo_tipo_socio,
    'cpf_representante_legal', t.cpf_representante_legal,
    'codigo_qualificacao_representante', t.codigo_qualificacao_representante
  ) AS properties
FROM (
  SELECT
    nu_cnpj_raiz AS cnpj_raiz,
    CASE
      WHEN (te_dados->>'identificadorSocio') = '1' THEN RIGHT(id_socio, 14)
      WHEN (te_dados->>'identificadorSocio') = '2' THEN RIGHT(id_socio, 11)
    END AS documento,
    (te_dados->>'pais')::smallint AS codigo_pais,
    TO_DATE(te_dados->>'entradaSociedade', 'YYYYMMDD') AS data_entrada_sociedade,
    (te_dados->>'qualificacaoSocio')::smallint AS codigo_qualificacao,
    (te_dados->>'identificadorSocio')::smallint AS codigo_tipo_socio,
    CASE WHEN
      te_dados->>'cpfRepresentanteLegal' IS NULL OR te_dados->>'cpfRepresentanteLegal' IN ('00000000000', '0', '') THEN NULL
      ELSE te_dados->>'cpfRepresentanteLegal'
    END AS cpf_representante_legal,
    (te_dados->>'qualificacaoRepresentanteLegal')::smallint AS codigo_qualificacao_representante
  FROM socios
) AS t

UNION ALL

SELECT
  person_uuid(RIGHT(TRIM(e.te_dados->>'nomeEmpresarial'), 11)) AS from_node_uuid,
  company_uuid(e.nu_cnpj_raiz) AS to_node_uuid,
  'is_partner' AS relationship,
  json_build_object() AS properties
FROM empresas AS e
  INNER JOIN mei_norm AS m
    ON e.nu_cnpj_raiz = m.cnpj_raiz
WHERE
  TRIM(e.te_dados->>'nomeEmpresarial') ~ ' [0-9.-]{11,14}$'
