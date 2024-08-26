WITH to_update AS (
  SELECT DISTINCT id_entidade AS cpf
  FROM eventos_atualizacao
  WHERE
    dt_evento BETWEEN '{{ start_datetime }}' AND '{{ end_datetime }}'
    AND nm_entidade IN ('PESSOA_FISICA')
)
SELECT
  person_uuid(cpf) AS object_uuid,
  NOW() AS updated_at,

  data_inscricao,
  codigo_situacao_cadastral,
  data_atualizacao,
  cpf,
  nome,
  nome_social,
  sexo,
  data_nascimento,
  ano_obito,
  municipio_nascimento,
  uf_nascimento,
  pais_nacionalidade,
  nome_mae,
  TRIM(
    COALESCE(tipo_logradouro, '') || ' '
    || COALESCE(logradouro, '') || ', '
    || COALESCE(numero_logradouro, '')
    || CASE WHEN complemento IS NOT NULL THEN ' (' || complemento || ')' ELSE '' END
    || ' - ' || COALESCE(bairro, '')
  ) AS endereco,
  municipio,
  uf,
  cep,
  TRIM(
    CASE WHEN ddi IS NOT NULL THEN '(' || ddi || ')' ELSE '' END
    || COALESCE(ddd::text, '')
    || ' ' || COALESCE(telefone, '')
  ) AS telefone,
  titulo_eleitoral,

  residente_exterior,
  pais_exterior,

  codigo_natureza_ocupacao,
  codigo_ocupacao_principal,
  ano_exercicio_ocupacao

FROM (
  SELECT
    RIGHT('00000000000' || nu_cpf, 11) AS cpf,

    parse_date(te_dados->>'dataAtualizacao') AS data_atualizacao,
    (te_dados->>'situacaoCadastral')::smallint AS codigo_situacao_cadastral,
    parse_date(te_dados->>'dataInscricao') AS data_inscricao,
    (te_dados->>'codigoUnidadeAdministrativa')::int AS codigo_unidade_administrativa,
    (te_dados->>'nomeUnidadeAdministrativa') AS unidade_administrativa,

    (te_dados->>'nome') AS nome,
    text_or_null(te_dados->>'nomeSocial') AS nome_social,
    (CASE
      WHEN (te_dados->>'sexo') = '1' THEN 'M'
      WHEN (te_dados->>'sexo') = '2' THEN 'F'
      WHEN (te_dados->>'sexo') = '9' THEN '?'
      ELSE NULL
    END)::"char" AS sexo,
    parse_date(te_dados->>'dataNascimento') AS data_nascimento,
    remove_zero(te_dados->>'anoObito')::smallint AS ano_obito,
    (te_dados->>'codigoMunicipioNaturalidade')::smallint AS codigo_municipio_naturalidade,
    (te_dados->>'nomeMunicipioNaturalidade') AS municipio_nascimento,
    (te_dados->>'ufMunicipioNaturalidade') AS uf_nascimento,
    text_or_null(te_dados->>'codigoPaisNacionalidade')::smallint AS codigo_pais_nacionalidade,
    (te_dados->>'nomePaisNacionalidade') AS pais_nacionalidade,
    text_or_null(te_dados->>'nomeMae') AS nome_mae,

    text_or_null(te_dados->>'tipoLogradouro') AS tipo_logradouro,
    text_or_null(te_dados->>'logradouro') AS logradouro,
    text_or_null(te_dados->>'numeroLogradouro') AS numero_logradouro,
    text_or_null(te_dados->>'complemento') AS complemento,
    text_or_null(te_dados->>'bairro') AS bairro,
    text_or_null(te_dados->>'codigoMunicipio')::smallint AS codigo_municipio,
    text_or_null(te_dados->>'municipio') AS municipio,
    text_or_null(te_dados->>'uf') AS uf,
    text_or_null(te_dados->>'cep') AS cep,

    CASE
      WHEN (te_dados->>'estrangeiro') = '0' THEN FALSE
      WHEN (te_dados->>'estrangeiro') = '1' THEN TRUE
      ELSE NULL
    END AS estrangeiro,
    CASE
      WHEN (te_dados->>'residenteExterior') = '1' THEN TRUE
      WHEN (te_dados->>'residenteExterior') = '2' THEN FALSE
      ELSE NULL
    END AS residente_exterior,
    text_or_null(te_dados->>'nomePaisExterior') AS pais_exterior,
    remove_zero(te_dados->>'codigoPaisExterior') AS codigo_pais_exterior,

    text_or_null(te_dados->>'ddi') AS ddi,
    text_or_null(te_dados->>'ddd')::smallint AS ddd,
    remove_zero(te_dados->>'telefone') AS telefone,

    remove_zero(te_dados->>'naturezaOcupacao')::smallint AS codigo_natureza_ocupacao,
    remove_zero(te_dados->>'ocupacaoPrincipal')::smallint AS codigo_ocupacao_principal,
    remove_zero(te_dados->>'exercicioOcupacao')::smallint AS ano_exercicio_ocupacao,

    text_or_null(te_dados->>'tituloEleitor') AS titulo_eleitoral,
    text_or_null(te_dados->>'erro') AS erro

  FROM cidadaos
  WHERE nu_cpf IN (SELECT cpf FROM to_update)
) AS t
