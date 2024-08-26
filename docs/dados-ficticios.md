# Importação de dados fictícios

Foram gerados dados fictícios para facilitar o teste e publicação de conteúdo do Sniper, sem expor pessoas reais.
Existe um script em `bin/mock_data_preparation.sh` que executa todo o processo de criação e importação dos dados
fictícios - se esse script for executado os passos abaixo não precisam ser executados.

## Gerando

Antes de importar, você precisa gerar os arquivos com os dados fictícios.
Os comandos abaixo irão gerar os objetos pessoas, empresas, candidaturas e as
relações de sociedade, candidatura e representação - devem ser executados no
container `web`:

```shell
python manage.py fakedata --quantity=100000 object Person data/fake-object-person.csv.xz
python manage.py fakedata --quantity=20000 object Company data/fake-object-company.csv.xz
python manage.py fakedata --quantity=50000 object Candidacy data/fake-object-candidacy.csv.xz
python manage.py fakedata --from-file=data/fake-object-person.csv.xz --to-file=data/fake-object-company.csv.xz --quantity=60000 relationship is_partner data/fake-relationship-is_partner.csv.xz
python manage.py fakedata --from-file=data/fake-object-company.csv.xz --to-file=data/fake-object-company.csv.xz --quantity=3000 relationship is_partner data/fake-relationship-is_partner-2.csv.xz
python manage.py fakedata --from-file=data/fake-object-company.csv.xz --to-file=data/fake-object-company.csv.xz --quantity=3000 relationship is_partner data/fake-relationship-is_partner-3.csv.xz
python manage.py fakedata --from-file=data/fake-object-person.csv.xz --to-file=data/fake-object-company.csv.xz --quantity=1000 relationship represents data/fake-relationship-represents.csv.xz
python manage.py fakedata --from-file=data/fake-object-person.csv.xz --to-file=data/fake-object-person.csv.xz --quantity=1000 relationship represents data/fake-relationship-represents-2.csv.xz
python manage.py fakedata --from-file=data/fake-object-person.csv.xz --to-file=data/fake-object-candidacy.csv.xz --quantity=75000 relationship runs_for data/fake-relationship-runs_for.csv.xz
```

> Nota: nem todos os dados estarão consistentes (por exemplo: uma candidatura
> estará ligada a mais de uma pessoa). Esse comportamento é proposital, para
> enfatizar o carácter fictício dos dados.


## Importando

Execute os seguintes comandos no terminal do container do backend (caso esteja
em ambiente de desenvolvimento: `docker compose exec web bash`):

```shell
# ATENÇÃO: os comandos abaixo DELETARÃO dados de objetos e relações pré-existentes!
# Primeiro, limpe as bases de dados:
echo "TRUNCATE TABLE urlid_graph_objectrepository RESTART IDENTITY CASCADE" | psql $DATABASE_URL
echo "TRUNCATE TABLE urlid_graph_elementconfig RESTART IDENTITY CASCADE" | psql $DATABASE_URL
echo "TRUNCATE TABLE urlid_graph_entity RESTART IDENTITY CASCADE" | psql $DATABASE_URL
echo "TRUNCATE TABLE dataset_person RESTART IDENTITY CASCADE" | psql $DATABASE_URL
echo "TRUNCATE TABLE dataset_company RESTART IDENTITY CASCADE" | psql $DATABASE_URL
echo "TRUNCATE TABLE dataset_candidacy RESTART IDENTITY CASCADE" | psql $DATABASE_URL
echo "DROP GRAPH IF EXISTS graph_db CASCADE; CREATE GRAPH IF NOT EXISTS graph_db;" | psql $GRAPH_DATABASE_URL

# Depois, crie as configurações iniciais:
python manage.py create_entities
python manage.py import_config config/element-config.csv

# Importe os objetos:
python manage.py import_objects dataset Person data/fake-object-person.csv.xz
python manage.py import_objects dataset Company data/fake-object-company.csv.xz
python manage.py import_objects dataset Candidacy data/fake-object-candidacy.csv.xz

# Importe as relações:
python manage.py import_relationships is_partner data/fake-relationship-is_partner.csv.xz
python manage.py import_relationships is_partner data/fake-relationship-is_partner-2.csv.xz
python manage.py import_relationships is_partner data/fake-relationship-is_partner-3.csv.xz
python manage.py import_relationships represents data/fake-relationship-represents.csv.xz
python manage.py import_relationships represents data/fake-relationship-represents-2.csv.xz
python manage.py import_relationships runs_for data/fake-relationship-runs_for.csv.xz
```

> Nota: enquanto os comandos de importação são executados você poderá
> acompanhar o status através dos modelos Job Log e Log Step no Django Admin
> (acessível em `/admin/`). Para criar um usuário administrativo, execute:
> `python manage.py createsuperuser`.
