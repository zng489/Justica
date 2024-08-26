from django.conf import settings

from dataset.management.commands.base_update import BaseObjectUpdateCommand


class Command(BaseObjectUpdateCommand):
    help = "Update dataset.Company objects based on another database"
    database_uri_from = settings.DATABASE_CNPJ_URL
    model = ("dataset", "Company")
    sql_filename = settings.BASE_DIR / "extractors" / "sql" / "update_object_company.sql"
