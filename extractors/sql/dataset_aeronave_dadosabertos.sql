SELECT
  CASE
    WHEN LENGTH(proprietario_documento) = 11 THEN person_uuid(proprietario_documento, proprietario)
    WHEN LENGTH(proprietario_documento) = 14 THEN company_uuid(proprietario_documento)
    ELSE uuid_nil()
  END AS object_uuid,
  CASE
    WHEN LENGTH(proprietario_documento) = 11 THEN 'Pessoa física'
    WHEN LENGTH(proprietario_documento) = 14 THEN 'Pessoa jurídica'
    ELSE NULL
  END AS tipo_proprietario,
  *
FROM (
  SELECT
    marca,
    proprietario,
    CASE
      WHEN LENGTH(cpf_cnpj) > 10 THEN REPLACE(REGEXP_REPLACE(cpf_cnpj, '[./-]', '', 'g'), 'X', '*')
      ELSE NULL
    END AS proprietario_documento,
    STRING_TO_ARRAY(outros_proprietarios, ';') AS outros_proprietarios,
    nm_operador AS operador,
    STRING_TO_ARRAY(outros_operadores, ';') AS outros_operadores,
    CASE
      WHEN LENGTH(cpf_cgc) > 10 THEN REPLACE(REGEXP_REPLACE(cpf_cgc, '[./-]', '', 'g'), 'X', '*')
      ELSE NULL
    END AS operador_documento,

    nm_fabricante AS fabricante,
    nr_ano_fabricacao::integer AS ano_fabricacao,
    ds_modelo AS modelo,
    nr_assentos::integer AS assentos,
    nr_tripulacao_min::integer AS tripulacao_minima,
    nr_passageiros_max::integer AS maximo_passageiros,
    nr_serie AS numero_serie,
    nr_cert_matricula::integer AS matricula,
    ds_motivo_canc AS motivo_cancelamento,
    dt_canc::date AS data_cancelamento_matricula,
    ds_gravame AS observacao
  FROM aeronave_dadosabertos_orig
) AS tmp
