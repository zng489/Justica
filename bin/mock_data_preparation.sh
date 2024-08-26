#!/bin/bash

BASE_DIR="/app"
MOCKDATA_CREATED_FLAG="/root/mock_data_created"

echo "======================="
echo "Initializing mock data...."
echo "======================="
cd ${BASE_DIR}

if [ -f ${MOCKDATA_CREATED_FLAG} ]; then
    echo "Mock data already created!!!!"
    exit 0
fi

echo "Creating entities:"
python manage.py create_entities
python manage.py import_config config/element-config.csv

if [ $? -ne 0 ]; then
    echo "Something failed during this step"
    exit $?
fi;

echo "Generating mock-data:"
python manage.py fakedata --quantity=100000 object Person ${BASE_DIR}/data/fake-object-person.csv.xz
python manage.py fakedata --quantity=20000 object Company ${BASE_DIR}/data/fake-object-company.csv.xz
python manage.py fakedata --quantity=50000 object Candidacy ${BASE_DIR}/data/fake-object-candidacy.csv.xz
python manage.py fakedata --from-file=${BASE_DIR}/data/fake-object-person.csv.xz --to-file=${BASE_DIR}/data/fake-object-company.csv.xz --quantity=60000 relationship is_partner ${BASE_DIR}/data/fake-relationship-is_partner.csv.xz
python manage.py fakedata --from-file=${BASE_DIR}/data/fake-object-company.csv.xz --to-file=${BASE_DIR}/data/fake-object-company.csv.xz --quantity=3000 relationship is_partner ${BASE_DIR}/data/fake-relationship-is_partner-2.csv.xz
python manage.py fakedata --from-file=${BASE_DIR}/data/fake-object-company.csv.xz --to-file=${BASE_DIR}/data/fake-object-company.csv.xz --quantity=3000 relationship is_partner ${BASE_DIR}/data/fake-relationship-is_partner-3.csv.xz
python manage.py fakedata --from-file=${BASE_DIR}/data/fake-object-person.csv.xz --to-file=${BASE_DIR}/data/fake-object-company.csv.xz --quantity=1000 relationship represents ${BASE_DIR}/data/fake-relationship-represents.csv.xz
python manage.py fakedata --from-file=${BASE_DIR}/data/fake-object-person.csv.xz --to-file=${BASE_DIR}/data/fake-object-person.csv.xz --quantity=1000 relationship represents ${BASE_DIR}/data/fake-relationship-represents-2.csv.xz
python manage.py fakedata --from-file=${BASE_DIR}/data/fake-object-person.csv.xz --to-file=${BASE_DIR}/data/fake-object-candidacy.csv.xz --quantity=75000 relationship runs_for ${BASE_DIR}/data/fake-relationship-runs_for.csv.xz

if [ $? -ne 0 ]; then
    echo "Something failed during this step"
    exit $?
fi;


echo "Importing all the mock-data:"
echo "Importing the objects:"
python manage.py import_objects dataset Person data/fake-object-person.csv.xz
python manage.py import_objects dataset Company data/fake-object-company.csv.xz
python manage.py import_objects dataset Candidacy data/fake-object-candidacy.csv.xz

echo "Importing the relationships:"
python manage.py import_relationships is_partner data/fake-relationship-is_partner.csv.xz
python manage.py import_relationships is_partner data/fake-relationship-is_partner-2.csv.xz
python manage.py import_relationships is_partner data/fake-relationship-is_partner-3.csv.xz
python manage.py import_relationships represents data/fake-relationship-represents.csv.xz
python manage.py import_relationships represents data/fake-relationship-represents-2.csv.xz
python manage.py import_relationships runs_for data/fake-relationship-runs_for.csv.xz

echo "Mock data successfully created!"
whoami
ls /root
echo "Changing the ${MOCKDATA_CREATED_FLAG}"
touch ${MOCKDATA_CREATED_FLAG}
echo "1" > ${MOCKDATA_CREATED_FLAG}
echo "======================="
