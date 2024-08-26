SELECT
  CASE
    WHEN LENGTH(documento) = 11 THEN person_uuid(documento, nome)
    WHEN LENGTH(documento) = 14 THEN company_uuid(documento)
    ELSE uuid_nil()
  END AS object_uuid,
  *
FROM sancao_orig
