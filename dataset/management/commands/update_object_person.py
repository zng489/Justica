from django.conf import settings

from dataset.management.commands.base_update import BaseObjectUpdateCommand


class Command(BaseObjectUpdateCommand):
    help = "Update dataset.Person objects based on another database"
    database_uri_from = settings.DATABASE_CPF_URL
    model = ("dataset", "Person")
    sql_filename = settings.BASE_DIR / "extractors" / "sql" / "update_object_person.sql"
