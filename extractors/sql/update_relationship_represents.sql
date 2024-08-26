WITH to_update AS (
  SELECT DISTINCT id_entidade AS cnpj_raiz
  FROM eventos_atualizacao
  WHERE
    dt_evento BETWEEN '{{ start_datetime }}' AND '{{ end_datetime }}'
    AND nm_entidade IN ('socio')
)
SELECT
  person_uuid(t.cpf_representante_legal) AS from_node_uuid,
  CASE
    WHEN t.codigo_tipo_socio = 1 THEN company_uuid(t.documento)
    WHEN t.codigo_tipo_socio = 2 THEN person_uuid(t.documento)
  END AS to_node_uuid,
  'represents' AS relationship,
  json_build_object(
    'cnpj_raiz', ARRAY_AGG(t.cnpj_raiz),
    'codigo_qualificacao_representante', ARRAY_AGG(t.codigo_qualificacao_representante)
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
      ELSE RIGHT('00000000000' || (te_dados->>'cpfRepresentanteLegal'), 11)
    END AS cpf_representante_legal,
    (te_dados->>'qualificacaoRepresentanteLegal')::smallint AS codigo_qualificacao_representante
  FROM socios
  WHERE nu_cnpj_raiz IN (SELECT cnpj_raiz FROM to_update)
) AS t
WHERE
  t.cpf_representante_legal IS NOT NULL
  AND t.documento IS NOT NULL
  AND t.codigo_tipo_socio IN (1, 2)
GROUP BY 1, 2
