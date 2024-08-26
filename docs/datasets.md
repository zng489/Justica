# Política de atualização de dados

O Sniper é composto dos seguintes tipos de datasets:

- Objetos (ícones apresentados no grafo, como pessoas físicas e jurídicas)
- Relações (flechas apresentadas no grafo, como de sociedade)
- Complementares (tabelas abertas ao selecionar um objeto, como lista de
  aeronaves)

Nem todos os datasets são guardados no banco de dados da plataforma (esses não
precisam de atualização, dado que são requisitados via API sob a demanda do
usuário). Cada dataset que precisa ser atualizado, deverá ser atualizado com
frequências diferentes; a forma como esses datasets são extraídos diferente de
um para outro, mas a importação é feita de maneira semelhante (através do
comando `python manage.py`).

Os objetos representados no grafo e seus dados complementares ficam armazenados
no banco de dados relacional PostgreSQL (variável de ambiente `$DATABASE_URL`),
já as relações e seus metadados, no AgensGraph (variável de ambiente
`$GRAPH_DATABASE_URL`).

Os dados utilizados no projeto devem ser extraídos das fontes originais
utilizando um padrão, onde cada objeto representado no grafo é referenciado por
seu UUID (mais detalhes sobre como gerar o UUID abaixo). Todos os datasets
devem ser declarados como modelos da aplicação `dataset` no arquivo
`dataset/models.py`. Na pasta `extractors/sql/` você encontra arquivos SQL
utilizados para extrair os datasets iniciais do projeto.


## Tipos de datasets

### Objetos

Os objetos são os ícones que aparecem diretamente no grafo. Cada um possui um
UUID gerado pela plataforma, que é usado para o cruzamento entre os diversos
datasets. Os objetos disponíveis atualmente são:

- Pessoas físicas (via convênio com Receita Federal)
- Empresas (via convênio com Receita Federal)
- Candidaturas políticas (dados abertos do Tribunal Superior Eleitoral)

### Relações

As relações são links entre objetos do grafo. As relações disponíveis
atualmente são:

- Sócio de empresa (via convênio com Receita Federal)
- Representante legal de sócio (via convênio com Receita Federal)
- Candidato (dados abertos do Tribunal Superior Eleitoral)

### Complementares

Datasets complementares

- Aeronaves (via parceria com ANAC)
- Bens declarados (dados abertos do Tribunal Superior Eleitoral)
- Embarcações (dados abertos do Tribunal Marítimo)
- Sanções (dados abertos do Portal da Transparência do Governo Federal)
- Resumo de processos (via API Cabeçalho Processual, sob demanda)

## Formato dos dados

Os arquivos importados deverão estar no formato CSV (podem estar compactados) e
devem seguir o seguinte schema:

### `Person`

- `nome`: `TextField`
- `nome_social`: `TextField`
- `cpf`: `TextField`
- `sexo`: `TextField`
- `titulo_eleitoral`: `TextField`
- `data_nascimento`: `DateField`
- `municipio_nascimento`: `TextField`
- `uf_nascimento`: `TextField`
- `pais_nacionalidade`: `TextField`
- `nome_mae`: `TextField`
- `endereco`: `TextField`
- `telefone`: `TextField`
- `ano_obito`: `PositiveSmallIntegerField`
- `residente_exterior`: `BooleanField`
- `pais_exterior`: `TextField`
- `codigo_natureza_ocupacao`: `PositiveSmallIntegerField`
- `codigo_ocupacao_principal`: `PositiveSmallIntegerField`
- `ano_exercicio_ocupacao`: `PositiveSmallIntegerField`

### `Company`

- `cnpj`: `TextField`
- `razao_social`: `TextField`
- `nome_fantasia`: `TextField`
- `cnae`: `ArrayField`
- `data_inicio_atividade`: `DateField`
- `data_situacao_cadastral`: `DateField`
- `codigo_situacao_cadastral`: `PositiveSmallIntegerField`
- `data_situacao_especial`: `TextField`
- `situacao_especial`: `TextField`
- `codigo_qualificacao_responsavel`: `PositiveSmallIntegerField`
- `capital_social`: `DecimalField`
- `codigo_porte`: `PositiveSmallIntegerField`
- `opcao_simples`: `BooleanField`
- `opcao_mei`: `BooleanField`
- `endereco`: `TextField`
- `bairro`: `TextField`
- `cep`: `TextField`
- `municipio`: `TextField`
- `uf`: `TextField`

### `Candidacy`

- `ano`: `IntegerField`
- `cargo`: `TextField`
- `nome_urna`: `TextField`
- `numero_sequencial`: `TextField`
- `sigla_partido`: `TextField`
- `sigla_unidade_federativa`: `TextField`
- `totalizacao_turno`: `TextField`
- `unidade_eleitoral`: `TextField`


### `BemDeclarado`

- `tipo`: `PositiveSmallIntegerField`
- `valor`: `DecimalField`
- `descricao`: `TextField`

### `Aeronave`

- `tipo_proprietario`: `TextField`
- `proprietario`: `TextField`
- `proprietario_documento`: `TextField`
- `outros_proprietarios`: `ArrayField`
- `operador`: `TextField`
- `outros_operadores`: `ArrayField`
- `operador_documento`: `TextField`
- `operador_uuid`: `UUIDField`
- `fabricante`: `TextField`
- `ano_fabricacao`: `PositiveSmallIntegerField`
- `modelo`: `TextField`
- `assentos`: `IntegerField`
- `tripulacao_minima`: `IntegerField`
- `maximo_passageiros`: `IntegerField`
- `numero_serie`: `TextField`
- `marca`: `CharField`
- `matricula`: `IntegerField`
- `motivo_cancelamento`: `TextField`
- `data_cancelamento_matricula`: `DateField`
- `observacao`: `TextField`
- `moeda`: `TextField`
- `valor`: `DecimalField`

### `Embarcacao`

- `reb`: `TextField`
- `nome`: `TextField`
- `data_registro`: `DateField`
- `data_validade`: `DateField`
- `proprietario`: `TextField`
- `rpm_tie_ait`: `TextField`
- `status`: `TextField`

### `Sancao`

- `nome`: `TextField`
- `documento`: `TextField`
- `processo`: `TextField`
- `tipo`: `TextField`
- `data_inicio`: `DateField`
- `data_final`: `DateField`
- `orgao`: `TextField`
- `fundamentacao`: `TextField`
- `multa`: `DecimalField`


## Comandos para importação

Antes de importar os dados, certifique-se de ter baixado/extraído a última
versão disponível de cada dataset.

Você poderá acompanhar a importação dos objetos e das relações e a indexação
dos objetos través do Django Admin (para o ambiente de homologação:
[sniper-api.stg.pdpj.jus.br/admin](https://sniper-api.stg.pdpj.jus.br/admin/)),
pelos modelos `Job log` e `Job step`.

> Nota: alguns datasets, como pessoas físicas e jurídicas, não são importados
> de arquivos e sim diretamente do banco de dados da Receita Federal. Esses
> datasets possuem comandos de importação próprios, como `manage.py
> import_person`, que fazem a conexão no banco original, transformam os dados e
> os inserem no banco do Sniper. Para os dados importados de arquivos, deve ser
> utilizado o formato CSV para importação dos dados, podendo estar
compactado em GZip (deve vir com o sufixo `.csv.gz`), BZip2 (deve vir com o
sufixo `.csv.bz2`) ou LZMA (deve vir com o sufixo `.csv.xz`).


### Objetos

```shell
python manage.py import_person
python manage.py import_pg2pg $DATABASE_CNPJ_URL "$(cat extractors/sql/object_company.sql)" Company
python manage.py import_objects dataset Candidacy data/object_candidacy.csv.xz
```

> Nota: pode ser necessário limpar as tabelas antes de efetuar a atualização,
> para evitar duplicidades, por exemplo: para remover as pessoas físicas
> cadastradas, execute no banco `$DATABASE_URL a consulta
> `TRUNCATE TABLE dataset_person RESTART IDENTITY CASCADE`.

### Relações

Primeiro é necessário gerar os arquivos das relações a partir das bases de
dados do TSE e da Receita Federal. Veja a seção "Exportando arquivos". Após
gerados os arquivos, eles poderão ser importados com o comando
`import_relationships`:

```shell
python manage.py import_relationships is_partner data/relationship_is_partner.csv.xz
python manage.py import_relationships represents data/relationship_represents.csv.xz
python manage.py import_relationships runs_for data/relationship_runs_for.csv.xz
```

> Nota: pode ser necessário limpar as relações antes de efetuar a
> atualização, para evitar duplicidades, por exemplo: para remover a relação
> `is_partner`, execute no banco `$GRAPH_DATABASE-URL` a consulta
> `MATCH ()-[r:is_partner]->() DELETE r`.

### Complementares

Siga os passos abaixo para baixar, converter e importar os datasets
complementares do Sniper:

#### Aeronaves

Baixar o relatório em TXT do sistema SACI, segundo formulário de exportação
mostrado ![nessa imagem](images/aeronave-export.png), salvá-lo em
`data/download/Relatorio.TXT` e executar os seguintes comandos:

```shell
# Corrigindo o arquivo de origem e convertendo para formato do SNIPER:
./aeronave.sh

# Caso a tabela desse dataset já esteja populada, limpe-a com:
echo "TRUNCATE TABLE dataset_aeronave RESTART IDENTITY CASCADE" | psql $DATABASE_URL

# O arquivo `data/output/dataset_aeronave.csv.gz` será gerado. Para importá-lo:
python manage.py import_objects dataset Aeronave data/output/dataset_aeronave.csv.gz
```

#### Embarcações

```shell
# Baixa e consolida dados do REB:
./embarcacao.sh

# Caso a tabela desse dataset já esteja populada, limpe-a com:
echo "TRUNCATE TABLE dataset_embarcacao RESTART IDENTITY CASCADE" | psql $DATABASE_URL

# O arquivo `data/output/dataset_embarcacao.csv.xz` será gerado. Para importá-lo:
python manage.py import_objects dataset Embarcacao data/output/dataset_embarcacao.csv.xz
```

#### Sanções

```shell
./sancao.sh

# O arquivo `data/output/dataset_sancao.csv.xz` será gerado. Para importá-lo:
python manage.py import_objects dataset Sancao data/output/dataset_sancao.csv.xz
```

#### Candidaturas e bens declarados

Primeiro, utilize o script de conversão/limpeza dos dados do TSE:

```shell
git clone https://github.com/turicas/eleicoes-brasil
cd eleicoes-brasil
pip install -r requirements.txt
python tse.py candidatura --years=2014,2016,2018,2020
python tse.py bem_declarado --years=2014,2016,2018,2020
rows pgimport --schema=schema/candidatura.csv data/output/candidatura.csv.gz $DATABASE_URL candidatura_orig
rows pgimport --schema=schema/bem_declarado.csv data/output/bem_declarado.csv.gz $DATABASE_URL bem_declarado_orig

rows pgexport --is-query $DATABASE_URL "$(cat extractors/sql/object_candidacy.sql)" ../data/object_candidacy.csv.xz
rows pgexport --is-query $DATABASE_URL "$(cat extractors/sql/dataset_bem_declarado.sql)" ../data/dataset_bem_declarado.csv.xz
rows pgexport --is-query $DATABASE_URL "$(cat relationship_runs_for.sql)" ../data/relationship_runs_for.csv.xz

echo "DROP TABLE candidatura_orig" | psql $DATABASE_URL
echo "DROP TABLE bem_declarado_orig" | psql $DATABASE_URL
cd ..
```

Agora, importe os dados:

```shell
python manage.py import_objects dataset Candidacy data/object_candidacy.csv.xz
python manage.py import_objects dataset BemDeclarado data/dataset_bem_declarado.csv.xz
python manage.py import_relationships runs_for data/relationship_runs_for.csv.xz
```

## Dados de Mapeamentos

Os mapeamentos utilizados pelo sistema estão em arquivos CSV no diretório
`dataset/mapping` e são carregados no arquivo `dataset/choices.py`. São eles:

- `bem-declarado-tipo.csv` (origem: TSE)
- `empresa-cnae.csv` (origem: dados abertos Receita Federal)
- `empresa-motivo-situacao-cadastral.csv` (origem: dados abertos Receita Federal)
- `empresa-natureza-juridica.csv` (origem: dados abertos Receita Federal)
- `empresa-porte.csv` (origem: dados abertos Receita Federal)
- `empresa-qualificacao-socio.csv` (origem: dados abertos Receita Federal)
- `empresa-situacao-cadastral.csv` (origem: dados abertos Receita Federal)
- `municipio.csv` (origem: dados abertos Receita Federal)
- `pais.csv` (origem: dados abertos Receita Federal)
- `pessoa-fisica-natureza-ocupacao.csv` (origem: extração de metadados do IRPF)
- `pessoa-fisica-ocupacao-principal.csv` (origem: extração de metadados do IRPF)
- `pessoa-fisica-situacao-cadastral.csv` (origem: pesquisa/análise da equipe de desenvolvimento)


## Integrando novos datasets

Para integrar novos datasets ao Sniper, precisa-se armazenar as informações com
o UUID do objeto em questão.

### Gerando UUIDs

Para que os dados possam ser identificados no grafo e relacionados, cria-se um
UUID para cada objeto seguindo a metodologia [URLid](https://urlid.org/), por
exemplo:

- Define-se uma URL inicial para representar o contexto do objeto (exemplo:
  `https://id.sniper.pdpj.jus.br/`)
- Define-se o tipo de entidade do objeto e sua versão (exemplo: `person`,
  versão `1`)
- Define-se qual informação única do objeto será usada (exemplo: 11 dígitos do
  CPF) e seleciona-se a informação (exemplo: `12345678901`)
- Monta-se a URL final, seguindo o padrão
  `https://base-url/entity-name/vX/internal-id/`, adicionando-se uma barra
  (`/`) ao fim (exemplo: `https://id.sniper.pdpj.jus.br/person/v1/12345678901/`)
- Executa-se o algoritmo UUID5 com o namespace URL
  (`6ba7b811-9dad-11d1-80b4-00c04fd430c8`) na URL gerada (resultado para a URL
  acima: `160a3f38-fed3-599e-9b91-88ecc56b5c23`)

No Sniper, as seguintes URLs devem ser utilizadas para referenciar os objetos:

- Pessoa física: `https://id.sniper.pdpj.jus.br/person/v1/<CPF-completo>/`
  (apenas dígitos, sem "." ou "-")
- Pessoa jurídica: `https://id.brasil.io/company/v1/<raiz-do-CNPJ>/` (8
  primeiros dígitos do CNPJ, sem ".", "/" ou "-")
- Candidatura: `https://id.brasil.io/candidacy/v1/<ano-eleição>-<número-sequencial>/`

> Nota: veja exemplos em `extractors/sql/`.


### Dados de objetos

Os modelos devem herdar de `urlid_graph.models.ObjectModelMixin` (que já possui
implicitamente o campo `object_uuid`, obrigatório, e `updated_at`, opcional).
A tabela pode conter mais de um registro para o mesmo `object_uuid` e é
esperado que seja uma tabela esparsa, dessa forma podemos adicionar várias
informações sobre o mesmo objeto (vindas de sistemas diferentes), que serão
consolidadas ao serví-lo pela API.

### Dados complementares de objetos

Os dados complementares serão listados para um objeto específico mostrado na
interface. Os modelos contendo esses dados devem herdar de
`urlid_graph.models.DatasetModel` (que já possui implicitamente o campo
`object_uuid`, obrigatório), além dos outros campos necessários ao dataset em
si.

A classe do modelo pode implementar métodos específicos de serialização (com a
assinatura `serialize_fieldname(self, value)`, onde `fieldname` é o nome do
campo declarado no modelo e `value` o valor que deverá ser serializado). Os
métodos de serialização serão automaticamente chamados pela API ao serializar o
objeto, não sendo necessária nenhuma outra implementação além do próprio modelo
para que a API já sirva requisições no endpoint
`/dataset/<dataset-slug>/<object-uuid>`, onde `<dataset-slug>` é o slug gerado
automaticamente a partir do nome da classe (`SomeModel` vira `some-model`) e
`<object-uuid>` o UUID do objeto da qual desejam-se os dados complementares.
