# backend/budget/management/commands/generate_api_docs.py

from django.core.management.base import BaseCommand
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions
import json

class Command(BaseCommand):
    help = 'Generates API documentation in Markdown format'

    def handle(self, *args, **options):
        # Create OpenAPI Info object
        info = openapi.Info(
            title="Family Budget API",
            default_version='v1',
            description="API documentation for the Family Budget Management App",
            terms_of_service="https://www.example.com/policies/terms/",
            contact=openapi.Contact(email="contact@example.com"),
            license=openapi.License(name="BSD License"),
        )

        # Generate OpenAPI schema
        generator = OpenAPISchemaGenerator(info=info)
        schema = generator.get_schema(request=None, public=True)

        # Convert OpenAPI schema to Markdown
        markdown_content = self.openapi_to_markdown(schema)

        # Write Markdown content to file
        with open('docs/API_documentation.md', 'w') as f:
            f.write(markdown_content)

        self.stdout.write(self.style.SUCCESS('API documentation generated successfully.'))

    def openapi_to_markdown(self, schema):
        md = f"# {schema.info.title}\n\n"
        md += f"Version: {schema.info.version}\n\n"
        md += f"{schema.info.description}\n\n"

        for path, path_item in schema.paths.items():
            md += f"## {path}\n\n"
            for method, operation in path_item.items():
                md += f"### {method.upper()}\n\n"
                if hasattr(operation, 'operation_id') and operation.operation_id:
                    md += f"{operation.operation_id}\n\n"
                if hasattr(operation, 'description') and operation.description:
                    md += f"{operation.description}\n\n"
                
                if hasattr(operation, 'parameters') and operation.parameters:
                    md += "#### Parameters\n\n"
                    for param in operation.parameters:
                        description = getattr(param, 'description', 'No description provided')
                        md += f"- `{param.name}` ({param.in_}): {description}\n"
                    md += "\n"

                if hasattr(operation, 'request_body') and operation.request_body:
                    md += "#### Request Body\n\n"
                    if hasattr(operation.request_body, 'content'):
                        content = operation.request_body.content.get('application/json')
                        if content and content.schema:
                            md += "```json\n"
                            md += json.dumps(self.simplify_schema(content.schema), indent=2)
                            md += "\n```\n\n"

                if hasattr(operation, 'responses') and operation.responses:
                    md += "#### Responses\n\n"
                    for status, response in operation.responses.items():
                        md += f"**{status}**\n\n"
                        if hasattr(response, 'description'):
                            md += f"{response.description}\n\n"
                        if hasattr(response, 'content'):
                            content = response.content.get('application/json')
                            if content and content.schema:
                                md += "```json\n"
                                md += json.dumps(self.simplify_schema(content.schema), indent=2)
                                md += "\n```\n\n"

            md += "---\n\n"

        return md

    def simplify_schema(self, schema):
        if isinstance(schema, openapi.Schema):
            return self.simplify_schema(schema.to_dict())
        elif isinstance(schema, dict):
            return {k: self.simplify_schema(v) for k, v in schema.items() if k != 'xml'}
        elif isinstance(schema, list):
            return [self.simplify_schema(item) for item in schema]
        else:
            return schema
