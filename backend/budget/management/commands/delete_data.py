from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps

class Command(BaseCommand):
    help = 'Deletes data from specified models'

    def handle(self, *args, **options):
        # Get a list of all models in the app
        models = list(apps.get_app_config('budget').get_models())

        # Print the list of models and prompt for user input
        self.stdout.write('Available models:')
        for i, model in enumerate(models, start=1):
            self.stdout.write(f'{i}. {model.__name__}')

        choices = input('Enter the numbers of the models you want to delete data from (comma-separated): ')
        choices = [int(c.strip()) for c in choices.split(',')]

        # Validate user input
        if not all(1 <= c <= len(models) for c in choices):
            self.stderr.write('Invalid model numbers.')
            return

        # Delete data from selected models in reverse order
        with transaction.atomic():
            for choice in reversed(choices):
                model = models[choice - 1]
                self.stdout.write(f'Deleting data from {model.__name__}...')
                model.objects.all().delete()

        self.stdout.write('Data deletion completed.')