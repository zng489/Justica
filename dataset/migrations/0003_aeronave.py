# Generated by Django 3.2.9 on 2022-01-17 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0002_bemdeclarado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aeronave',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_uuid', models.UUIDField(db_index=True, help_text='UUID of described object', verbose_name='Object UUID')),
                ('tipo_proprietario', models.TextField(blank=True, null=True)),
                ('proprietario', models.TextField(blank=True, null=True)),
                ('proprietario_documento', models.TextField(blank=True, null=True)),
                ('outros_proprietarios', models.TextField(blank=True, null=True)),
                ('operador', models.TextField(blank=True, null=True)),
                ('outros_operadores', models.TextField(blank=True, null=True)),
                ('operador_documento', models.TextField(blank=True, null=True)),
                ('fabricante', models.TextField(blank=True, null=True)),
                ('ano_fabricacao', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('modelo', models.TextField(blank=True, null=True)),
                ('assentos', models.IntegerField(blank=True, null=True)),
                ('tripulacao_minima', models.IntegerField(blank=True, null=True)),
                ('maximo_passageiros', models.IntegerField(blank=True, null=True)),
                ('numero_serie', models.TextField(blank=True, null=True)),
                ('matricula', models.IntegerField(blank=True, null=True)),
                ('motivo_cancelamento', models.TextField(blank=True, null=True)),
                ('data_cancelamento_matricula', models.DateField(blank=True, null=True)),
                ('observacao', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
