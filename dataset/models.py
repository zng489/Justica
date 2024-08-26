import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from urlid_graph.models import DatasetModel, ObjectModelMixin

from dataset import serializers  # noqa
from dataset import choices, formatting

NULL_UUID = uuid.UUID(int=0)


def display_str(value):
    if isinstance(value, int):
        return ""
    return value


def get_names_for_objects(object_uuids):
    cache_key = tuple(sorted(set(object_uuids)))
    names = get_names_for_objects.__cache.get(cache_key)
    if names is None:
        names = {object_uuid: set() for object_uuid in object_uuids}

        found_people = Person.objects.filter(object_uuid__in=object_uuids).values("object_uuid", "nome")
        for person in found_people:
            name = str(person["nome"] or "").strip()
            if name:
                names[person["object_uuid"]].add(name)

        # Try to find a Company with this object_uuid to get its names
        found_companies = Company.objects.filter(object_uuid__in=object_uuids).values("object_uuid", "razao_social")
        for company in found_companies:
            name = str(company["razao_social"] or "").strip()
            if name:
                names[company["object_uuid"]].add(name)

        get_names_for_objects.__cache[cache_key] = names
        if len(get_names_for_objects.__cache) > 500:
            get_names_for_objects.__cache = {}
    return names


get_names_for_objects.__cache = {}


class Person(ObjectModelMixin):
    id = models.AutoField(primary_key=True)

    data_inscricao = models.DateField(null=True, blank=True)
    codigo_situacao_cadastral = models.SmallIntegerField(
        null=True, blank=True, choices=choices.PESSOA_FISICA_SITUACAO_CADASTRAL
    )
    data_atualizacao = models.DateField(null=True, blank=True)
    nome = models.TextField(null=True, blank=True)
    nome_social = models.TextField(null=True, blank=True)
    cpf = models.TextField(max_length=11, null=True, blank=True, db_index=True)
    sexo = models.TextField(max_length=1, null=True, blank=True)
    titulo_eleitoral = models.TextField(max_length=12, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    municipio_nascimento = models.TextField(max_length=63, null=True, blank=True)
    uf_nascimento = models.TextField(max_length=2, null=True, blank=True)
    pais_nacionalidade = models.TextField(null=True, blank=True)
    nome_mae = models.TextField(null=True, blank=True)
    endereco = models.TextField(null=True, blank=True)
    municipio = models.TextField(max_length=63, null=True, blank=True)
    uf = models.TextField(max_length=2, null=True, blank=True)
    cep = models.TextField(max_length=8, null=True, blank=True)
    telefone = models.TextField(null=True, blank=True)
    ano_obito = models.SmallIntegerField(null=True, blank=True)
    residente_exterior = models.BooleanField(null=True, blank=True)
    pais_exterior = models.TextField(null=True, blank=True)
    codigo_natureza_ocupacao = models.SmallIntegerField(
        null=True, blank=True, choices=choices.PESSOA_FISICA_NATUREZA_OCUPACAO
    )
    codigo_ocupacao_principal = models.SmallIntegerField(
        null=True, blank=True, choices=choices.PESSOA_FISICA_OCUPACAO_PRINCIPAL
    )
    ano_exercicio_ocupacao = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        entity_name = "person"
        entity_uuid = "31364cbd-0662-55f8-bcd5-27be67de1c8a"
        search_fields = ["nome", "nome_social"]
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"

    def __str__(self):
        cpf = formatting.format_cpf(self.cpf)
        return f"{cpf} {self.nome}"

    def serialize(self, related_objects=None, *args, **kwargs):
        endereco = self.endereco
        if self.municipio:
            endereco += f", {self.municipio}"
        if self.uf:
            endereco += f"/{self.uf}"
        if self.cep:
            endereco += f" ({self.cep})"
        naturalidade = (
            f"{self.municipio_nascimento}/{self.uf_nascimento}"
            if self.municipio_nascimento and self.uf_nascimento
            else None
        )
        data = {
            "Nome": self.nome,
            "CPF": formatting.format_cpf(self.cpf),
            "Data de inscrição": formatting.format_date(self.data_inscricao),
            "Título eleitoral": formatting.format_titulo_eleitoral(self.titulo_eleitoral),
            "Data de nascimento": formatting.format_date(self.data_nascimento),
            "Naturalidade": naturalidade,
            "Nome social": self.nome_social,
            "Nacionalidade": self.pais_nacionalidade,
            "Nome da mãe": self.nome_mae,
            "Endereço": formatting.format_address(endereco),
            "Telefone": formatting.format_phone(self.telefone),
            "Ano do óbito": self.ano_obito,
            "Sexo": formatting.format_sex(self.sexo),
            "País de residência": self.pais_exterior,
        }

        title, value = "Situação cadastral", display_str(self.get_codigo_situacao_cadastral_display())
        if self.data_atualizacao:
            title += f" ({formatting.format_date(self.data_atualizacao)})"
        data[title] = value

        if self.codigo_natureza_ocupacao and self.codigo_ocupacao_principal:
            title = "Ocupação"
            if self.ano_exercicio_ocupacao:
                title += f" ({self.ano_exercicio_ocupacao})"
            value = ""
            if self.codigo_natureza_ocupacao:
                value = display_str(self.get_codigo_natureza_ocupacao_display())
            if self.codigo_ocupacao_principal:
                ocupacao = display_str(self.get_codigo_ocupacao_principal_display())
                if ocupacao:
                    value = f"{value} / {ocupacao}" if value else ocupacao
            data[title] = value

        data["extra"] = {}
        for model_name in "Aeronave Embarcacao Sancao".split():
            related = (related_objects or {}).get(model_name, []) or []
            if len(related) > 0:
                data["extra"][model_name.lower()] = True

        return {key: value for key, value in data.items() if value or key == "extra"}

    @classmethod
    def related_querysets(cls, object_uuids):
        return {
            "Aeronave": Aeronave.objects.for_objects(object_uuids),
            "Embarcacao": Embarcacao.objects.for_objects(object_uuids),
            "Sancao": Sancao.objects.for_objects(object_uuids),
        }


class Company(ObjectModelMixin):
    id = models.AutoField(primary_key=True)

    cnpj = models.TextField(max_length=14, null=True, blank=True, db_index=True)
    razao_social = models.TextField(max_length=255, null=True, blank=True)
    nome_fantasia = models.TextField(max_length=255, null=True, blank=True)
    cnae = ArrayField(
        models.TextField(max_length=7, null=True, blank=True, choices=choices.EMPRESA_CNAE), null=True, blank=True
    )
    data_cadastro = models.DateField(null=True, blank=True)
    data_situacao_cadastral = models.DateField(null=True, blank=True)
    codigo_situacao_cadastral = models.SmallIntegerField(
        null=True, blank=True, choices=choices.EMPRESA_SITUACAO_CADASTRAL
    )
    codigo_motivo_situacao_cadastral = models.SmallIntegerField(
        null=True, blank=True, choices=choices.EMPRESA_MOTIVO_SITUACAO_CADASTRAL
    )
    situacao_especial = models.TextField(max_length=31, null=True, blank=True)
    data_situacao_especial = models.TextField(null=True, blank=True)
    codigo_natureza_juridica = models.SmallIntegerField(
        null=True, blank=True, choices=choices.EMPRESA_NATUREZA_JURIDICA
    )
    codigo_porte = models.SmallIntegerField(null=True, blank=True, choices=choices.EMPRESA_PORTE)
    capital_social = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    opcao_simples = models.BooleanField(null=True, blank=True)
    opcao_mei = models.BooleanField(null=True, blank=True)
    codigo_qualificacao_responsavel = models.SmallIntegerField(
        null=True, blank=True, choices=choices.EMPRESA_QUALIFICACAO_SOCIO
    )
    cpf_responsavel = models.TextField(max_length=255, null=True, blank=True)

    endereco = models.TextField(max_length=255, null=True, blank=True)
    codigo_municipio = models.SmallIntegerField(null=True, blank=True, choices=choices.MUNICIPIO)
    uf = models.TextField(max_length=2, null=True, blank=True)
    cep = models.TextField(max_length=8, null=True, blank=True)
    cidade_exterior = models.TextField(max_length=255, null=True, blank=True)
    codigo_pais = models.SmallIntegerField(null=True, blank=True, choices=choices.PAIS)

    telefone_1 = models.TextField(max_length=255, null=True, blank=True)
    telefone_2 = models.TextField(max_length=255, null=True, blank=True)
    email = models.TextField(max_length=255, null=True, blank=True)

    class Meta:
        entity_name = "company"
        entity_uuid = uuid.uuid5(uuid.NAMESPACE_URL, "https://id.brasil.io/company/v1/")
        search_fields = ["razao_social", "nome_fantasia"]
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        cnpj = formatting.format_cnpj(self.cnpj)
        return f"{cnpj} {self.razao_social}"

    def serialize(self, related_objects=None, *args, **kwargs):
        endereco = self.endereco
        if self.codigo_municipio:
            municipio = display_str(self.get_codigo_municipio_display())
            if municipio:
                endereco += f", {municipio}"
        if self.uf:
            endereco += f"/{self.uf}"
        if self.cep:
            endereco += f" ({self.cep})"
        telefones = [item for item in (self.telefone_1, self.telefone_2) if item]
        data = {
            "CNPJ": formatting.format_cnpj(self.cnpj),
            "Razão social": self.razao_social,
            "Nome fantasia": self.nome_fantasia,
            "Data de cadastro": formatting.format_date(self.data_cadastro),
            "Natureza jurídica": display_str(self.get_codigo_natureza_juridica_display()),
            "CPF do(a) responsável": formatting.format_cpf(self.cpf_responsavel),
            "Qualificação do responsável": display_str(self.get_codigo_qualificacao_responsavel_display()),
            "Capital social": formatting.format_currency_brl(self.capital_social),
            "Porte": display_str(self.get_codigo_porte_display()),
            "Opção pelo Simples": formatting.format_bool(self.opcao_simples),
            "Opção pelo MEI": formatting.format_bool(self.opcao_mei),
            "Endereço": formatting.format_address(endereco),
            "Cidade exterior": self.cidade_exterior,
            "País": display_str(self.get_codigo_pais_display()),
            "Telefone(s)": ", ".join(telefones),
            "E-mail": self.email,
        }

        if self.cnae:
            title = "Atividades econômicas" if len(self.cnae) > 1 else "Atividade econômica"
            value = "; ".join(formatting.format_cnae(cnae) for cnae in self.cnae) if self.cnae else None
            data[title] = value

        if self.codigo_situacao_cadastral:
            title = "Situação cadastral"
            if self.data_situacao_cadastral:
                title += f" ({formatting.format_date(self.data_situacao_cadastral)})"
            value = display_str(self.get_codigo_situacao_cadastral_display())
            if self.codigo_motivo_situacao_cadastral:
                motivo = display_str(self.get_codigo_motivo_situacao_cadastral_display())
                if motivo:
                    value = f"{value} ({motivo})" if value else motivo
            data[title] = value

        if self.situacao_especial:
            title = "Situação especial"
            if self.data_situacao_especial:
                # date = formatting.format_date(self.data_situacao_especial)
                # TODO: move back to formatted date
                title += f" ({self.data_situacao_especial})"
            data[title] = self.situacao_especial

        data["extra"] = {}
        for model_name in "Aeronave Embarcacao Sancao".split():
            related = (related_objects or {}).get(model_name, []) or []
            if len(related) > 0:
                data["extra"][model_name.lower()] = True

        return {key: value for key, value in data.items() if value or key == "extra"}

    @classmethod
    def related_querysets(cls, object_uuids):
        return {
            "Aeronave": Aeronave.objects.for_objects(object_uuids),
            "Embarcacao": Embarcacao.objects.for_objects(object_uuids),
            "Sancao": Sancao.objects.for_objects(object_uuids),
        }


class Candidacy(ObjectModelMixin):
    id = models.AutoField(primary_key=True)

    ano = models.IntegerField(null=True, blank=True)
    cargo = models.TextField(max_length=31, null=True, blank=True)
    nome_urna = models.TextField(max_length=31, null=True, blank=True)
    numero_sequencial = models.TextField(max_length=15, null=True, blank=True)
    sigla_partido = models.TextField(max_length=15, null=True, blank=True)
    sigla_unidade_federativa = models.TextField(max_length=2, null=True, blank=True)
    totalizacao_turno = models.TextField(max_length=16, null=True, blank=True)
    unidade_eleitoral = models.TextField(max_length=32, null=True, blank=True)

    class Meta:
        entity_name = "candidacy"
        entity_uuid = uuid.uuid5(uuid.NAMESPACE_URL, "https://id.brasil.io/candidacy/v1/")
        search_fields = ["nome_urna", "cargo"]
        verbose_name = "Candidatura"
        verbose_name_plural = "Candidaturas"

    def serialize(self, related_objects=None, *args, **kwargs):
        data = {
            "Ano": self.ano,
            "Cargo": self.cargo,
            "Nome na urna": self.nome_urna,
            "Número sequencial": formatting.format_numero_sequencial(self.numero_sequencial),
            "Partido": self.sigla_partido,
            "UF": self.sigla_unidade_federativa,
            "Resultado no turno": self.totalizacao_turno,
            "Unidade eleitoral": self.unidade_eleitoral,
        }

        data["extra"] = {}
        for model_name in "Aeronave Embarcacao Sancao".split():
            related = (related_objects or {}).get(model_name, []) or []
            if len(related) > 0:
                data["extra"][model_name.lower()] = True

        return {key: value for key, value in data.items() if value or key == "extra"}


class BemDeclarado(DatasetModel):
    id = models.AutoField(primary_key=True)

    tipo = models.SmallIntegerField(
        choices=choices.BEM_DECLARADO_TIPO, verbose_name="Tipo", help_text="Tipo do bem declarado"
    )
    valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Valor",
        help_text="Valor do bem",
    )
    descricao = models.TextField(
        max_length=512,
        null=True,
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição do bem",
    )

    class Meta:
        slug = "bem-declarado"
        ordering = ["-valor"]
        verbose_name = "Bem declarado"
        verbose_name_plural = "Bens declarados"

    @classmethod
    def extra(cls, qs):
        total = qs.aggregate(total=models.Sum("valor"))["total"]
        return {
            "title": "Bens declarados",
            "description": "Os bens abaixo foram declarados ao TSE:",
            "total": formatting.format_currency_brl(total),
        }

    def serialize_tipo(self, value):
        return display_str(self.get_tipo_display())

    def serialize_valor(self, value):
        return formatting.format_currency_brl(value)


class AeronaveQuerySet(models.QuerySet):
    def for_object(self, object_uuid):
        return self.for_objects([object_uuid])

    def for_objects(self, object_uuids):
        names = get_names_for_objects(object_uuids)
        all_names = []
        for object_uuid in object_uuids:
            all_names.extend(names.get(object_uuid, []))
        query = (
            models.Q(object_uuid__in=object_uuids)
            | models.Q(operador_uuid__in=object_uuids)
            | (
                models.Q(object_uuid=NULL_UUID)
                & (
                    models.Q(proprietario__in=all_names)
                    | models.Q(outros_proprietarios__overlap=all_names)
                    | models.Q(operador__in=all_names)
                    | models.Q(outros_operadores__overlap=all_names)
                )
            )
        )
        return self.filter(query)


class Aeronave(DatasetModel):
    objects = AeronaveQuerySet.as_manager()

    id = models.AutoField(primary_key=True)
    tipo_proprietario = models.TextField(null=True, blank=True, verbose_name="Tipo de proprietário")
    proprietario = models.TextField(null=True, blank=True, db_index=True, verbose_name="Proprietário(a)")
    proprietario_documento = models.TextField(null=True, blank=True, verbose_name="CPF/CNPJ proprietário(a)")
    outros_proprietarios = ArrayField(
        models.TextField(),
        db_index=True,
        null=True,
        blank=True,
        verbose_name="Outros proprietários",
    )
    operador = models.TextField(null=True, blank=True, verbose_name="Operador(a)")
    operador_uuid = models.UUIDField(null=True, blank=True, verbose_name="ID do(a) operador(a)", db_index=True)
    outros_operadores = ArrayField(models.TextField(), null=True, blank=True, verbose_name="Outros operadores")
    operador_documento = models.TextField(null=True, blank=True, verbose_name="CPF/CNPJ operador(a)")
    fabricante = models.TextField(null=True, blank=True, verbose_name="Fabricante")
    ano_fabricacao = models.SmallIntegerField(null=True, blank=True, verbose_name="Ano de fabricação")
    modelo = models.TextField(null=True, blank=True, verbose_name="Modelo")
    assentos = models.IntegerField(null=True, blank=True, verbose_name="Qtd.  assentos")
    tripulacao_minima = models.IntegerField(null=True, blank=True, verbose_name="Tripulação mín.")
    maximo_passageiros = models.IntegerField(null=True, blank=True, verbose_name="Máx. passageiros")
    numero_serie = models.TextField(null=True, blank=True, verbose_name="Número de série")
    marca = models.CharField(max_length=5, null=False, blank=False, verbose_name="Marca")
    matricula = models.IntegerField(null=True, blank=True, verbose_name="Matrícula")
    motivo_cancelamento = models.TextField(null=True, blank=True, verbose_name="Motivo do cancelamento")
    data_cancelamento_matricula = models.DateField(null=True, blank=True, verbose_name="Data de cancelamento")
    observacao = models.TextField(null=True, blank=True, verbose_name="Observação")
    moeda = models.TextField(null=True, blank=True, verbose_name="Moeda")
    valor = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor")

    class Meta:
        verbose_name = "Aeronave"
        verbose_name_plural = "Aeronaves"

    def serialize_proprietario_documento(self, value):
        return formatting.format_cpf_cnpj(value)

    def serialize_operador_documento(self, value):
        return formatting.format_cpf_cnpj(value)

    def serialize_outros_proprietarios(self, value):
        if value is None:
            return None
        return ", ".join(value)

    def serialize_outros_operadores(self, value):
        if value is None:
            return None
        return ", ".join(value)

    def serialize_data_cancelamento_matricula(self, value):
        return formatting.format_date(value)

    @classmethod
    def extra(cls, qs):
        return {
            "title": "Aeronaves",
            "description": (
                "De acordo com a ANAC, a(s) aeronave(s) listada(s) abaixo "
                "foi(ram) registrada(s) no documento do objeto em questão."
            ),
        }


class EmbarcacaoQuerySet(models.QuerySet):
    def for_object(self, object_uuid):
        return self.for_objects([object_uuid])

    def for_objects(self, object_uuids):
        names = get_names_for_objects(object_uuids)
        all_names = []
        for object_uuid in object_uuids:
            all_names.extend(names.get(object_uuid, []))
        query = models.Q(object_uuid__in=object_uuids) | (
            models.Q(object_uuid=NULL_UUID) & models.Q(proprietario__in=all_names)
        )
        return self.filter(query)


class Embarcacao(DatasetModel):
    objects = EmbarcacaoQuerySet.as_manager()

    id = models.AutoField(primary_key=True)
    reb = models.TextField(verbose_name="REB")
    nome = models.TextField(verbose_name="Nome")
    data_registro = models.DateField(verbose_name="Data de registro")
    data_validade = models.DateField(null=True, blank=True, verbose_name="Validade")
    proprietario = models.TextField(db_index=True, verbose_name="Proprietário(a)")
    rpm_tie_ait = models.TextField(null=True, blank=True, verbose_name="RPM/TIE/AIT")
    status = models.TextField(null=True, blank=True, verbose_name="Status")

    class Meta:
        verbose_name = "Embarcação"
        verbose_name_plural = "Embarcações"

    def serialize_data_validade(self, value):
        return formatting.format_date(value)

    def serialize_data_registro(self, value):
        return formatting.format_date(value)

    @classmethod
    def extra(cls, qs):
        return {
            "title": "Embarcações",
            "description": (
                "Lista de embarcações registradas no Tribunal Marítimo "
                "vinculadas ao nome desse objeto. "
                "Atenção: o vínculo é feito através do nome e, no caso de "
                "homônimos, o sistema pode identificar o vínculo de maneira "
                "incorreta, sendo necessária checagem no órgão responsável."
            ),
        }


class SancaoQuerySet(models.QuerySet):
    def for_object(self, object_uuid):
        return self.for_objects([object_uuid])

    def for_objects(self, object_uuids):
        return self.filter(object_uuid__in=object_uuids)


class Sancao(DatasetModel):
    objects = SancaoQuerySet.as_manager()

    id = models.AutoField(primary_key=True)

    nome = models.TextField(verbose_name="Nome")
    documento = models.TextField(verbose_name="CPF/CNPJ")
    processo = models.TextField(verbose_name="Processo")
    tipo = models.TextField(verbose_name="Tipo")
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data de início")
    data_final = models.DateField(null=True, blank=True, verbose_name="Data final")
    orgao = models.TextField(verbose_name="Órgão")
    fundamentacao = models.TextField(null=True, blank=True, verbose_name="Fundamentação")
    multa = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Multa")

    class Meta:
        verbose_name = "Sanção"
        verbose_name_plural = "Sanções"

    def serialize_data_inicio(self, value):
        return formatting.format_date(value)

    def serialize_data_final(self, value):
        return formatting.format_date(value)

    def serialize_multa(self, value):
        return formatting.format_currency_brl(value)

    def serialize_documento(self, value):
        return formatting.format_cpf_cnpj(value)

    @classmethod
    def extra(cls, qs):
        return {
            "title": "Sanções",
            "description": (
                "Lista de sanções da Controladoria Geral da União: "
                "Empresas inidôneas e suspensas, Entidades sem fins "
                "lucrativos impedidas, Empresas punidas e Acordos de leniência."
            ),
        }
