import uuid

from django.core.management.base import BaseCommand
from urlid_graph.models import Entity


class Command(BaseCommand):
    help = "Create Brasil.IO entities"

    def handle(self, *args, **options):
        brasilio_base_url = "https://id.brasil.io/"
        sniper_base_url = "https://id.sniper.pdpj.jus.br/"
        entities = (
            (sniper_base_url, "person"),
            (brasilio_base_url, "company"),
            (brasilio_base_url, "candidacy"),
        )
        version = 1
        for base_url, name in entities:
            url = f"{base_url}{name}/v{version}/"
            row = {
                "base_url": base_url,
                "name": name,
                "version": version,
                "uuid": uuid.uuid5(uuid.NAMESPACE_URL, url),
            }
            obj = Entity.objects.filter(**row).first()
            created = False
            if obj is None:
                obj = Entity(**row)
                obj.save()
                created = True
            print(f"{'CREATED' if created else 'ALREADY EXISTS'} {name}, uuid = {obj.uuid}")
