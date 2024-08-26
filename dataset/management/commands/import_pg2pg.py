import traceback

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from rows.plugins.postgresql import pg2pg
from urlid_graph.log import ImportObjectsLogger
from urlid_graph.models import ObjectModelMixin, ObjectRepository


class Command(BaseCommand):
    help = "Import objects based on another database (instead of CSV)"

    def add_arguments(self, parser):
        parser.add_argument("--no-index", action="store_true", help="Do not run indexing step to ObjectRepository")
        parser.add_argument("--batch-size", type=int, default=100_000, help="Number of rows to index per turn")
        parser.add_argument("database_uri_from")
        parser.add_argument("query")
        parser.add_argument("model")

    def handle(self, *args, **kwargs):
        should_index = not kwargs["no_index"]
        batch_size = kwargs["batch_size"]
        database_uri_from = kwargs["database_uri_from"]
        query = kwargs["query"]
        model = kwargs["model"]

        Model = apps.get_model("dataset", model)
        last_object = Model.objects.order_by("-id").first()
        start_id = last_object.id + 1 if last_object is not None else None

        self.logger = ImportObjectsLogger(description=f"pg2pg -> {model}")
        print(f"Starting job {self.logger.job.id}")

        def update_progress(done, total):
            # done is actually the last step done and total the total_done
            self.logger.progress(done=total, total=None)

        self.logger.start_step("import")
        try:
            import_status = pg2pg(
                database_uri_from=database_uri_from,
                database_uri_to=settings.DATABASE_URL,
                table_name_from=query,
                table_name_to=Model._meta.db_table,
                callback=update_progress,
            )
        except:  # noqa
            self.logger.error(traceback.format_exc())

        else:
            message = f"Total rows imported: {import_status.get('rows_imported')}"
            print(message)
            self.logger.finish_step("import", message=message)

        if should_index and issubclass(Model, ObjectModelMixin):
            self.logger.start_step("index", message=f"start_id: {start_id}, batch_size: {batch_size}")

            try:
                ObjectRepository.objects.index(
                    Model,
                    start_id=start_id,
                    batch_size=batch_size,
                    callback=self.logger.progress,
                )
            except:  # noqa
                self.logger.error(traceback.format_exc())
            finally:
                self.logger.finish_step("index")

        self.logger.finish()
