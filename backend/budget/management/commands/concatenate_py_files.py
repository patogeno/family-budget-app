from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import datetime
import json
import fnmatch
import os

def parse_gitignore(gitignore_path):
    ignore_patterns = []
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as gitignore_file:
            for line in gitignore_file:
                line = line.strip()
                if line and not line.startswith('#'):
                    ignore_patterns.append(line)
    return ignore_patterns

def should_ignore(file_path, ignore_patterns, root_dir):
    relative_path = file_path.relative_to(root_dir)
    
    for pattern in ignore_patterns:
        # Handle patterns starting with '/'
        if pattern.startswith('/'):
            if fnmatch.fnmatch(str(relative_path), pattern[1:]):
                return True
        # Handle directory patterns ending with '/'
        elif pattern.endswith('/'):
            if any(part == pattern[:-1] for part in relative_path.parts):
                return True
        # Handle file patterns and patterns with wildcards
        elif fnmatch.fnmatch(str(relative_path), pattern) or \
             any(fnmatch.fnmatch(part, pattern) for part in relative_path.parts):
            return True
    return False

class Command(BaseCommand):
    help = 'Concatenates selected Python files into a single output file.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Select all .py files in the project.',
        )
        parser.add_argument(
            '--previous',
            action='store_true',
            help='Use the previous selection of files.',
        )

    def get_selection_from_user(self, all_files, previous_selection):
        for i, file in enumerate(all_files):
            selected_mark = "(previously selected)" if str(file) in previous_selection else ""
            self.stdout.write(f"{i+1}: {file} {selected_mark}")
        self.stdout.write(f"{len(all_files) + 1}: Select all")
        self.stdout.write(f"{len(all_files) + 2}: Use previous selection")
        selected_indices = input("Enter the numbers of the files to include (comma-separated), select all, or use previous: ")

        if str(len(all_files) + 1) in selected_indices.split(','):
            return [str(f) for f in all_files]
        elif str(len(all_files) + 2) in selected_indices.split(','):
            return previous_selection
        else:
            selection_indices = [int(i) - 1 for i in selected_indices.split(',')]
            return [str(all_files[i]) for i in selection_indices if i < len(all_files)]

    def handle(self, *args, **options):
        config_file = Path('file_selection_config.json')
        root_dir = Path('.')
        root_gitignore = root_dir / '.gitignore'
        frontend_gitignore = root_dir / 'frontend' / '.gitignore'

        ignore_patterns = parse_gitignore(root_gitignore) + parse_gitignore(frontend_gitignore)

        all_files = [file for file in root_dir.rglob('*.py') 
                     if not should_ignore(file, ignore_patterns, root_dir)]

        previous_selection = []

        if config_file.exists():
            with open(config_file) as f:
                previous_selection = json.load(f)

        if options['all']:
            selection = [str(f) for f in all_files]
        elif options['previous']:
            selection = previous_selection if previous_selection else [str(f) for f in all_files]
        else:
            selection = self.get_selection_from_user(all_files, previous_selection)

        # Save the selection for future use
        with open(config_file, 'w') as f:
            json.dump(selection, f)

        # Concatenate files
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = f"concatenated_{timestamp}.py"
        with open(output_file, 'w') as outfile:
            for file_path in selection:
                with open(file_path) as infile:
                    outfile.write(f"## file: {file_path} ##\n")
                    outfile.write(infile.read() + '\n\n')

        self.stdout.write(self.style.SUCCESS(f'Successfully concatenated files into {output_file}'))

        # Debug output
        self.stdout.write("Ignore patterns:")
        for pattern in ignore_patterns:
            self.stdout.write(f"  {pattern}")
        self.stdout.write(f"Total Python files found: {len(all_files)}")
        self.stdout.write("First 10 Python files:")
        for file in all_files[:10]:
            self.stdout.write(f"  {file}")