SELECT
  CASE
    WHEN proprietario_documento IN ('00000000000', '00000000000000') THEN uuid_nil()
    WHEN LENGTH(proprietario_documento) = 11 THEN person_uuid(proprietario_documento)
    WHEN LENGTH(proprietario_documento) = 14 THEN company_uuid(proprietario_documento)
    ELSE uuid_nil()
  END AS object_uuid,
  CASE
    WHEN operador_documento IN ('00000000000', '00000000000000') THEN uuid_nil()
    WHEN LENGTH(operador_documento) = 11 THEN person_uuid(operador_documento)
    WHEN LENGTH(operador_documento) = 14 THEN company_uuid(operador_documento)
    ELSE uuid_nil()
  END AS operador_uuid,
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
      WHEN proprietario_tipo_pessoa = 'F' THEN RIGHT('00000000000' || cpf_cnpj, 11)
      WHEN proprietario_tipo_pessoa = 'J' THEN RIGHT('00000000000000' || cpf_cnpj, 14)
      ELSE NULL
    END AS proprietario_documento,
    STRING_TO_ARRAY(outros_proprietarios, ',') AS outros_proprietarios,

    nm_operador AS operador,
    STRING_TO_ARRAY(outros_operadores, ',') AS outros_operadores,
    CASE
      WHEN cpf_cgc = '0' OR cpf_cgc IS NULL THEN NULL
      WHEN operador_tipo_pessoa = 'F' THEN RIGHT('00000000000' || cpf_cgc, 11)
      WHEN operador_tipo_pessoa = 'J' THEN RIGHT('00000000000000' || cpf_cgc, 14)
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
    CASE
      WHEN LENGTH(dt_canc) != 8 OR dt_canc LIKE '% %' THEN NULL
      ELSE to_date(dt_canc, 'DDMMYYYY')
    END AS data_cancelamento_matricula,
    ds_gravame AS observacao,
    moeda AS moeda,
    CASE
      WHEN valor ~ '[,.][0-9]{2}$' THEN REGEXP_REPLACE(valor, '[^0-9]', '', 'g')::bigint / 100.0
      ELSE NULL
    END AS valor

  FROM aeronave_orig
  WHERE
    cpf_cnpj <> '0'
    AND cpf_cnpj IS NOT NULL
) AS tmp
