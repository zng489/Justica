import random
import uuid

CNPJ_MULTIPLIERS_1 = tuple(int(x) for x in "543298765432")
CNPJ_MULTIPLIERS_2 = tuple(int(x) for x in "6543298765432")


def uuid_from_document(document):
    """Generate object UUID from CPF/CNPJ"""
    # TODO: clean document up?
    doctype, object_uuid = None, None
    if len(document) == 11:
        object_uuid = uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"https://id.sniper.pdpj.jus.br/person/v1/{document}/",
        )
        doctype = "cpf"
    elif len(document) == 14:
        object_uuid = uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"https://id.brasil.io/company/v1/{document[:8]}/",
        )
        doctype = "cnpj"
    return doctype, object_uuid


def cpf_checks(text):
    """
    >>> cpf_checks("111111111xx")
    '11'

    >>> cpf_checks("123456789xx")
    '09'
    """
    check_1 = str(((sum(int(c) * (10 - i) for i, c in enumerate(text[:9])) * 10) % 11) % 10)
    check_2 = str(((sum(int(c) * (11 - i) for i, c in enumerate(text[:9] + check_1)) * 10) % 11) % 10)
    return check_1 + check_2


def random_cpf():
    digits = "".join(str(random.randint(0, 9)) for _ in range(9))
    return digits + cpf_checks(digits)


def cnpj_checks(text):
    check_1 = sum(int(c) * m for c, m in zip(text[:12], CNPJ_MULTIPLIERS_1)) % 11
    check_1 = str(11 - check_1 if check_1 >= 2 else 0)
    check_2 = sum(int(c) * m for c, m in zip(text[:12] + check_1, CNPJ_MULTIPLIERS_2)) % 11
    check_2 = str(11 - check_2 if check_2 >= 2 else 0)
    return check_1 + check_2


def random_cnpj():
    digits = "".join(str(random.randint(0, 9)) for _ in range(8)) + "0001"
    return digits + cnpj_checks(digits)
