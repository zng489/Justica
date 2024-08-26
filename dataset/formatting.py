import re

from django.contrib.humanize.templatetags.humanize import intcomma

from dataset import choices

REGEXP_NOT_NUMBERS = re.compile("[^0-9*]")
REGEXP_CEP = re.compile(r"(.*)\(([0-9]{8})\)")
CNAE = dict(choices.EMPRESA_CNAE)


def format_address(value):
    value = str(value or "").strip()
    if not value:
        return None
    result = REGEXP_CEP.findall(value)
    if result:
        cep = result[0][1]
        cep = f"{cep[:2]}.{cep[2:5]}-{cep[5:]}"
        value = f"{result[0][0].strip()} ({cep})"
    return value


def format_bool(value):
    return {
        None: None,
        True: "Sim",
        False: "Não",
    }[value]


def format_cnae(value):
    if value:
        if len(value) == 7:
            value_fmt = f"{value[:4]}-{value[4:5]}/{value[5:]}"
        else:
            value_fmt = value
    if value in CNAE:
        value_fmt += f" {CNAE[value]}"
    return value_fmt


def format_cnpj(value):
    value = str(value or "").strip()
    if not value:
        return None
    value = f"{int(REGEXP_NOT_NUMBERS.sub('', value)):014d}"

    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:14]}"


def format_cpf(value):
    value = str(value or "").strip()
    if not value:
        return None
    value = REGEXP_NOT_NUMBERS.sub("", value)
    if "*" not in value:
        value = f"{int(value):011d}"
    elif len(value) < 11:
        value = "0" * (11 - len(value)) + value

    return f"{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:11]}"


def clean_cpf(value):
    return re.sub(r"[.-]", "", value)


def format_cpf_cnpj(value):
    """
    >>> format_cpf_cnpj("123456789xy")
    '123.456.789-xy'
    >>> format_cpf_cnpj("12345678qwerxz")
    '12.345.678/qwer-xz'
    >>> format_cpf_cnpj("12.345.678/qwer-xz")
    '12.345.678/qwer-xz'
    >>> format_cpf_cnpj("1234")
    '1234'
    """
    value = str(value or "").replace(".", "").replace("-", "").replace("/", "").strip()
    if not value:
        return ""
    elif len(value) == 11:  # CPF
        return f"{value[0:3]}.{value[3:6]}.{value[6:9]}-{value[9:]}"
    elif len(value) == 14:  # CNPJ
        return f"{value[0:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"
    else:
        return value


def format_currency_brl(value):
    if not value:
        return None
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_date(value):
    if value is None:
        return None
    return value.strftime("%d/%m/%Y")


def format_datetime(value):
    if value is None:
        return None
    return value.strftime("%d/%m/%Y %H:%M:%S")


def format_numero_sequencial(value):
    return intcomma(value)


def format_numero_processo(value):
    """
    >>> format_numero_processo('12345678901234567890')
    '0000012-34.5678.9.01.2345'
    """
    if "." in value:
        return value

    value = str(value or "").strip()
    if not value:
        return ""

    v = "0" * (20 - len(value)) + value
    return f"{v[:7]}-{v[7:9]}.{v[9:13]}.{v[13:14]}.{v[14:16]}.{v[16:20]}"


def format_phone(value):
    value = str(value or "").strip()
    if not value or len(value) < 8:
        return None
    return value


def format_sex(value):
    value = str(value or "").strip()
    if not value:
        return None
    return {"F": "Feminino", "M": "Masculino"}.get(value)


def format_titulo_eleitoral(value):
    value = str(value or "").strip()
    if not value:
        return None
    value = f"{int(REGEXP_NOT_NUMBERS.sub('', value)):012d}"

    return f"{value[:4]}.{value[4:8]}.{value[8:10]}-{value[10:12]}"
