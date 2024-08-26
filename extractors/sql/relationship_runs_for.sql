SELECT
  person_uuid(c.cpf) AS from_node_uuid,
  candidacy_uuid(c.ano::smallint, c.numero_sequencial) AS to_node_uuid,
  'runs_for' AS relationship,
  json_build_object() AS properties
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
