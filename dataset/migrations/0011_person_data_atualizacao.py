# Generated by Django 3.2.9 on 2022-07-02 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0010_auto_20220627_0557'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='data_atualizacao',
            field=models.DateField(blank=True, null=True),
        ),
    ]