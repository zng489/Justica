# Generated by Django 3.2.9 on 2022-02-25 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0007_auto_20220225_0840'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sancao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_uuid', models.UUIDField(db_index=True, help_text='UUID of described object', verbose_name='Object UUID')),
                ('nome', models.TextField(verbose_name='Nome')),
                ('documento', models.TextField(verbose_name='CPF/CNPJ')),
                ('processo', models.TextField(verbose_name='Processo')),
                ('tipo', models.TextField(verbose_name='Tipo')),
                ('data_inicio', models.DateField(blank=True, null=True, verbose_name='Data de início')),
                ('data_final', models.DateField(blank=True, null=True, verbose_name='Data final')),
                ('orgao', models.TextField(verbose_name='Órgão')),
                ('fundamentacao', models.TextField(blank=True, null=True, verbose_name='Fundamentação')),
                ('multa', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Multa')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='aeronave',
            name='operador_documento',
            field=models.TextField(blank=True, null=True, verbose_name='CPF/CNPJ operador(a)'),
        ),
        migrations.AlterField(
            model_name='aeronave',
            name='proprietario_documento',
            field=models.TextField(blank=True, null=True, verbose_name='CPF/CNPJ proprietário(a)'),
        ),
    ]
