# Generated by Django 3.2.9 on 2021-11-19 13:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialLogin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('keycloak', 'keycloak')], max_length=30, verbose_name='provider')),
                ('uid', models.CharField(max_length=191, verbose_name='uid')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='last login')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('extra_data', models.JSONField(default=dict, verbose_name='extra data')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]