CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- String parsing functions
CREATE OR REPLACE FUNCTION parse_date(value TEXT)
RETURNS DATE AS $$
BEGIN
  RETURN CASE
    WHEN value NOT IN ('00000000', '0') THEN TO_DATE(value, 'YYYYMMDD')
    ELSE NULL
  END;
EXCEPTION
  WHEN others THEN RETURN NULL::date;
END; $$ LANGUAGE 'plpgsql' IMMUTABLE;

CREATE OR REPLACE FUNCTION text_or_null(value TEXT)
RETURNS TEXT AS $$
BEGIN
  RETURN CASE
    WHEN value <> '' THEN value
    ELSE NULL
 END;
END; $$ LANGUAGE 'plpgsql' IMMUTABLE;

CREATE OR REPLACE FUNCTION remove_zero(value TEXT)
RETURNS TEXT AS $$
BEGIN
  RETURN CASE
    WHEN value <> '0' THEN value
    ELSE NULL
 END;
END; $$ LANGUAGE 'plpgsql' IMMUTABLE;


-- URLid-related functions
CREATE OR REPLACE FUNCTION person_uuid(cpf TEXT)
RETURNS UUID AS $$
BEGIN
  RETURN uuid_generate_v5(uuid_ns_url(), 'https://id.sniper.pdpj.jus.br/person/v1/' || cpf || '/');
END; $$ LANGUAGE 'plpgsql' IMMUTABLE;

CREATE OR REPLACE FUNCTION company_uuid(cnpj TEXT)
RETURNS UUID AS $$
BEGIN
  RETURN uuid_generate_v5(uuid_ns_url(), 'https://id.brasil.io/company/v1/' || LEFT(cnpj, 8) || '/');
END; $$ LANGUAGE 'plpgsql' IMMUTABLE;

CREATE OR REPLACE FUNCTION candidacy_uuid(ano INT, numero_sequencial TEXT)
RETURNS UUID AS $$
BEGIN
  RETURN uuid_generate_v5(uuid_ns_url(), 'https://id.brasil.io/candidacy/v1/' || ano::text || '-' || regexp_replace(numero_sequencial, '[^0-9]', '', 'g') || '/');
END; $$ LANGUAGE 'plpgsql' IMMUTABLE;
