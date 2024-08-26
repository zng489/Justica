import datetime
import traceback

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import Context, Template
from django.utils import timezone
from rows.plugins.postgresql import pg2pg
from urlid_graph.log import AsyncLogger, Step
from urlid_graph.models import ObjectModelMixin, ObjectRepository

from dataset.management.commands.base_import import Progress


def parse_date(value):
    value = str(value or "").strip()
    if not value:
        return None
    return datetime.datetime.strptime(value, "%Y-%m-%d").date()


class UpdateObjectsLogger(AsyncLogger):
    name = "updating objects"
    steps = [
        Step("pre-import", "Disable indexes etc."),
        Step("import", "Import data into table"),
        Step("delete-old-objects", "Delete old versions of updated objects"),
        Step("index", "Index imported objects in ObjectRepository"),
        Step("post-import", "Re-enable indexes etc."),
    ]


class BaseObjectUpdateCommand(BaseCommand):
    help = None
    database_uri_from = None
    model = (None, None)
    sql_filename = None

    def add_arguments(self, parser):
        today = timezone.now()
        tomorrow = today + datetime.timedelta(days=1)
        last_month = today - datetime.timedelta(days=30)
        parser.add_argument("--start-date", type=parse_date, default=last_month.date())
        parser.add_argument("--end-date", type=parse_date, default=tomorrow.date())
        parser.add_argument("--no-index", action="store_true", help="Do not run indexing step to ObjectRepository")
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100_000,
            help="Number of rows to index per turn (does not affect number of imported rows)",
        )

    def handle(self, *args, **kwargs):
        should_index = not kwargs["no_index"]
        batch_size = kwargs["batch_size"]
        start_date = kwargs["start_date"]
        end_date = kwargs["end_date"]
        with self.sql_filename.open() as fobj:
            self.template = Template(fobj.read())
        self.Model = apps.get_model(*self.model)
        start_id = self.get_checkpoint()

        self.logger = UpdateObjectsLogger(
            description=f"pg2pg update {self.Model.__name__} (start={start_date}, end={end_date}, start_id={start_id})"
        )
        print(f"Starting job {self.logger.job.id} (start ID: {start_id})")
        self.import_data(start_date=start_date, end_date=end_date)
        self.delete_old_objects(start_id=start_id)
        if should_index and issubclass(self.Model, ObjectModelMixin):
            self.index_objects(start_id=start_id, batch_size=batch_size)
        self.logger.finish()

    def get_checkpoint(self):
        """Get the next sequential ID for the model, so we can track which objects to index"""
        last_object = self.Model.objects.order_by("-id").first()
        start_id = last_object.id + 1 if last_object is not None else None
        return start_id

    def query(self, start_date, end_date):
        """Render the SQL query to be run on remote database, using start and end date"""
        return self.template.render(
            Context(
                {
                    "start_datetime": f"{start_date.strftime('%Y-%m-%d')} 00:00:00+00:00",
                    "end_datetime": f"{end_date.strftime('%Y-%m-%d')} 00:00:00+00:00",
                }
            )
        )

    def import_data(self, start_date, end_date):
        """Execute pg2pg to import rows from remote database to the local one"""
        progress = Progress(self.logger)
        self.logger.start_step("import")
        try:
            query = self.query(start_date, end_date)
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
            message = "Finished with error"
        else:
            rows_imported = import_status.get("rows_imported", 0)
            message = f"Total rows imported: {rows_imported}"
        self.logger.finish_step("import", message=message)

    def delete_old_objects(self, start_id):
        """Delete old versions of imported objects"""
        self.logger.start_step("delete-old-objects")
        new_objects_uuids = self.Model.objects.filter(id__gte=start_id).values_list("object_uuid")
        rows_deleted, _ = self.Model.objects.filter(id__lt=start_id, object_uuid__in=new_objects_uuids).delete()
        self.logger.finish_step("delete-old-objects", message=f"Deleted {rows_deleted} old objects")

    def index_objects(self, start_id, batch_size):
        """Index objects so they will be accessible in full-text search"""
        self.logger.start_step("index", message=f"start_id: {start_id}, batch_size: {batch_size}")
        try:
            ObjectRepository.objects.index(
                self.Model,
                start_id=start_id,
                batch_size=batch_size,
                callback=self.logger.progress,
            )
        except:  # noqa
            self.logger.error(traceback.format_exc())
        finally:
            self.logger.finish_step("index")
