import os
from django.core.management.base import BaseCommand
from pathlib import Path
from budget.utils import parse_gitignore, should_ignore

class Command(BaseCommand):
    help = 'Generate a folder tree of the project, respecting .gitignore files and ignoring .git folder'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, help='Output file path')

    def handle(self, *args, **options):
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        output_file = options['output'] or 'folder_tree.txt'

        root_gitignore = project_root / '.gitignore'
        frontend_gitignore = project_root / 'frontend' / '.gitignore'

        ignore_patterns = parse_gitignore(root_gitignore) + parse_gitignore(frontend_gitignore)

        with open(output_file, 'w', encoding='utf-8') as f:
            for root, dirs, files in os.walk(project_root):
                root_path = Path(root)
                level = len(root_path.relative_to(project_root).parts)
                indent = '│   ' * (level - 1) + '├── '
                
                # Ignore .git folder
                if '.git' in root_path.parts:
                    continue
                
                if not should_ignore(root_path, ignore_patterns, project_root):
                    f.write(f'{indent}{root_path.name}/\n')
                    
                    for file in files:
                        file_path = root_path / file
                        if not should_ignore(file_path, ignore_patterns, project_root):
                            f.write(f'{indent}│   {file}\n')

                # Remove .git from dirs to prevent walking into it
                if '.git' in dirs:
                    dirs.remove('.git')

        self.stdout.write(self.style.SUCCESS(f'Folder tree generated in {output_file}'))