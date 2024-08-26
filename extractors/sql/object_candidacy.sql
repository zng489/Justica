SELECT
  candidacy_uuid(c.ano::int, c.numero_sequencial) AS object_uuid,
  c.data_eleicao AS updated_at,
  c.ano,
  c.cargo,
  c.nome_urna,
  c.numero_sequencial,
  c.sigla_partido,
  c.sigla_unidade_federativa,
  c.totalizacao_turno,
  c.unidade_eleitoral
FROM (
  SELECT
    ano,
    numero_sequencial,
    MAX(turno) AS turno
  FROM candidatura_orig
  WHERE
    ano >= 2014
    AND cpf IS NOT NULL
  GROUP BY 1, 2
) AS t
  LEFT JOIN candidatura_orig AS c ON
    c.ano = t.ano
    AND c.numero_sequencial = t.numero_sequencial
    AND c.turno = t.turno
