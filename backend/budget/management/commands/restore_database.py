from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
import os
import json

class Command(BaseCommand):
    help = 'Restore the database from a backup file using Django loaddata'

    def add_arguments(self, parser):
        parser.add_argument('backup_file', type=str, help='Path to the backup file')

    def handle(self, *args, **options):
        backup_file = options['backup_file']

        if not os.path.exists(backup_file):
            self.stderr.write(self.style.ERROR(f'Backup file {backup_file} does not exist'))
            return

        try:
            # Preserve content types
            self.stdout.write("Preserving content types...")
            content_types = list(ContentType.objects.all().values())

            # Flush the database
            self.stdout.write("Flushing the database...")
            call_command('flush', '--no-input')

            # Restore content types
            self.stdout.write("Restoring content types...")
            ContentType.objects.all().delete()
            ContentType.objects.bulk_create([ContentType(**data) for data in content_types])

            # Reset the primary keys for all tables
            self.stdout.write("Resetting primary keys...")
            with connection.cursor() as cursor:
                for model in apps.get_models():
                    if not model._meta.managed or not model._meta.auto_field:
                        continue
                    table = model._meta.db_table
                    try:
                        cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), 1, false);")
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Couldn't reset sequence for {table}: {str(e)}"))

            # Load the data from the backup, excluding content types
            self.stdout.write("Loading data from backup...")
            with open(backup_file, 'r') as f:
                data = json.load(f)
            filtered_data = [item for item in data if item['model'] != 'contenttypes.contenttype']
            with open('filtered_backup.json', 'w') as f:
                json.dump(filtered_data, f)
            call_command('loaddata', 'filtered_backup.json')
            os.remove('filtered_backup.json')
            
            self.stdout.write(self.style.SUCCESS(f'Successfully restored database from {backup_file}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An error occurred while restoring the database: {str(e)}'))