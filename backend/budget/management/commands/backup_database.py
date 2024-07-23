from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Backup the database using Django dumpdata'

    def handle(self, *args, **options):
        backup_dir = 'database_backups'
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'{backup_dir}/backup_{timestamp}.json'

        try:
            with open(backup_file, 'w') as f:
                call_command('dumpdata', '--all', '--indent', '4', stdout=f)
            self.stdout.write(self.style.SUCCESS(f'Successfully backed up database to {backup_file}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An error occurred while backing up the database: {str(e)}'))