from django.conf import settings

from dataset.management.commands.base_import import ImportCommand


class Command(ImportCommand):
    help = "Import dataset.Person objects based on another database"
    database_uri_from = settings.DATABASE_CPF_URL
    model = ("dataset", "Person")
    split_field = "cpf"
    sql_filename = settings.BASE_DIR / "extractors" / "sql" / "object_person.sql"

    def get_checkpoint(self):
        start_id, first_value = super().get_checkpoint()
        if first_value:
            first_value = str(int(first_value))
        return start_id, first_value
