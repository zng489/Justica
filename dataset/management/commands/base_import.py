import traceback

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import Context, Template
from rows.plugins.postgresql import pg2pg
from urlid_graph.log import ImportObjectsLogger
from urlid_graph.models import ObjectModelMixin, ObjectRepository


class Progress:
    """Update logger saving internal total_done (reusable between calls to pg2pg)"""

    def __init__(self, logger):
        self.total_done = 0
        self.logger = logger

    def update(self, done, total):
        # done is actually the last step done and total the total_done
        self.total_done += total
        self.logger.progress(done=self.total_done, total=None)


class ImportCommand(BaseCommand):
    help = "Import objects based on another database"
    database_uri_from = None
    model = (None, None)  # app_name, Model
    split_field = None  # field_name
    sql_filename = None  # settings.BASE_DIR / "file.sql"

    def add_arguments(self, parser):
        parser.add_argument("--no-index", action="store_true", help="Do not run indexing step to ObjectRepository")
        parser.add_argument("--batch-size", type=int, default=100_000, help="Number of rows to import/index per turn")

        with self.sql_filename.open() as fobj:
            self.template = Template(fobj.read())

    def query(self, first_value, limit):
        return self.template.render(Context({self.split_field: first_value, "limit": limit}))

    def get_checkpoint(self):
        last_object = self.Model.objects.order_by("-id").first()
        start_id = last_object.id + 1 if last_object is not None else None
        first_value = getattr(last_object, self.split_field) if last_object is not None else ""
        return start_id, first_value

    def handle(self, *args, **kwargs):
        should_index = not kwargs["no_index"]
        batch_size = kwargs["batch_size"]
        self.Model = apps.get_model(*self.model)

        self.logger = ImportObjectsLogger(description=f"pg2pg -> {self.Model.__name__}")
        print(f"Starting job {self.logger.job.id}")

        progress = Progress(self.logger)
        self.logger.start_step("import")
        first_start_id, rows_imported = None, 0
        while True:
            start_id, first_value = self.get_checkpoint()
            if first_start_id is None:
                first_start_id = start_id
            print(start_id, first_value)
            query = self.query(first_value, batch_size)
            try:
                import_status = pg2pg(
                    database_uri_from=self.database_uri_from,
                    database_uri_to=settings.DATABASE_URL,
                    table_name_from=query,
                    table_name_to=self.Model._meta.db_table,
                    callback=progress.update,
                    create_table=False,
                )
            except:  # noqa
                self.logger.error(traceback.format_exc())
                break
            else:
                last_rows_imported = import_status.get("rows_imported", 0)
                rows_imported += last_rows_imported
                if last_rows_imported < batch_size:
                    break

        message = f"Total rows imported: {rows_imported}"
        print(message)
        self.logger.finish_step("import", message=message)

        if should_index and issubclass(self.Model, ObjectModelMixin):
            self.logger.start_step("index", message=f"start_id: {start_id}, batch_size: {batch_size}")

            try:
                ObjectRepository.objects.index(
                    self.Model,
                    start_id=first_start_id,
                    batch_size=batch_size,
                    callback=self.logger.progress,
                )
            except:  # noqa
                self.logger.error(traceback.format_exc())
            finally:
                self.logger.finish_step("index")

        self.logger.finish()
