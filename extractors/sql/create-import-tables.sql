DROP TABLE IF EXISTS import_empresas;
CREATE TABLE import_empresas (
    nu_cnpj_raiz character varying(8) NOT NULL,
    te_dados jsonb
);

DROP TABLE IF EXISTS import_simples;
CREATE TABLE import_simples (
    nu_cnpj_raiz character varying(8) NOT NULL,
    te_dados jsonb
);

DROP TABLE IF EXISTS import_socios;
CREATE TABLE import_socios (
    nu_cnpj_raiz character varying(8) NOT NULL,
    id_socio character varying(14) NOT NULL,
    te_dados jsonb
);

DROP TABLE IF EXISTS import_estabelecimentos;
CREATE TABLE import_estabelecimentos (
    id_estabelecimento character varying(8) NOT NULL,
    nu_cnpj_raiz character varying(8) NOT NULL,
    te_dados jsonb
);

DROP TABLE IF EXISTS import_cidadaos;
CREATE TABLE import_cidadaos (
    nu_cpf character varying NOT NULL,
    te_dados jsonb
);
