from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
import os

class Command(BaseCommand):
    help = 'Generates a Draw.io diagram of the project models'

    def handle(self, *args, **options):
        # Generate the GraphViz dot file
        output_file = 'models_diagram.dot'
        call_command('graph_models', all_applications=True, output=output_file)

        # Convert the dot file to Draw.io format
        os.system(f'dot -Tsvg {output_file} -o models_diagram.svg')

        self.stdout.write(self.style.SUCCESS('Models diagram generated successfully.'))