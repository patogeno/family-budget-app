from django.core.management.base import BaseCommand
from pathlib import Path
import datetime
import json
import os
from budget.utils import parse_gitignore, should_ignore

class Command(BaseCommand):
    help = 'Concatenates selected Python files, assets, and generates a folder tree'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Select all files in the project.',
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
        config_file = Path('project_selection_config.json')
        root_dir = Path('.')
        root_gitignore = root_dir / '.gitignore'
        frontend_gitignore = root_dir / 'frontend' / '.gitignore'

        ignore_patterns = parse_gitignore(root_gitignore) + parse_gitignore(frontend_gitignore)

        all_files = []
        for ext in ['.py', '.html', '.css', '.scss', '.js', '.md']:
            all_files.extend(file for file in root_dir.rglob(f'*{ext}') 
                             if not should_ignore(file, ignore_patterns, root_dir))

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
        output_file_py = f"concatenated_py_{timestamp}.py"
        output_file_assets = f"concatenated_assets_{timestamp}.txt"
        output_file_md = f"concatenated_md_{timestamp}.md"
        output_file_tree = f"folder_tree_{timestamp}.txt"

        py_files = [f for f in selection if f.endswith('.py')]
        md_files = [f for f in selection if f.endswith('.md')]
        other_files = [f for f in selection if not f.endswith('.py') and not f.endswith('.md')]

        # Concatenate Python files
        with open(output_file_py, 'w') as outfile:
            for file_path in py_files:
                with open(file_path) as infile:
                    outfile.write(f"## file: {file_path} ##\n")
                    outfile.write(infile.read() + '\n\n')

        # Concatenate non-MD asset files
        with open(output_file_assets, 'w') as outfile:
            for file_path in other_files:
                with open(file_path) as infile:
                    outfile.write(f"file: {file_path}\n")
                    outfile.write(infile.read() + '\n\n')

        # Concatenate MD files
        with open(output_file_md, 'w') as outfile:
            for file_path in md_files:
                with open(file_path) as infile:
                    outfile.write(f"# file: {file_path}\n\n")
                    outfile.write(infile.read() + '\n\n')

        # Generate folder tree
        with open(output_file_tree, 'w', encoding='utf-8') as f:
            for root, dirs, files in os.walk(root_dir):
                root_path = Path(root)
                level = len(root_path.relative_to(root_dir).parts)
                indent = '│   ' * (level - 1) + '├── '
                
                if '.git' in root_path.parts:
                    continue
                
                if not should_ignore(root_path, ignore_patterns, root_dir):
                    f.write(f'{indent}{root_path.name}/\n')
                    
                    for file in files:
                        file_path = root_path / file
                        if not should_ignore(file_path, ignore_patterns, root_dir):
                            f.write(f'{indent}│   {file}\n')

                if '.git' in dirs:
                    dirs.remove('.git')

        self.stdout.write(self.style.SUCCESS(f'Successfully concatenated Python files into {output_file_py}'))
        self.stdout.write(self.style.SUCCESS(f'Successfully concatenated non-MD assets into {output_file_assets}'))
        self.stdout.write(self.style.SUCCESS(f'Successfully concatenated MD files into {output_file_md}'))
        self.stdout.write(self.style.SUCCESS(f'Folder tree generated in {output_file_tree}'))