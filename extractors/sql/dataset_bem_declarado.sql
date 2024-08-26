SELECT
  candidacy_uuid(ano::integer, numero_sequencial) AS object_uuid,
  codigo_tipo AS tipo,
  valor AS valor,
  detalhe AS descricao
FROM bem_declarado_orig
WHERE ano >= 2014
ORDER BY numero_ordem ASC
