# Family Budget Management App

## Overview
This is a web application for personal use to manage the family's fortnightly, monthly, and yearly budget and expenses more effectively. The app allows tracking income sources, categorizing expenses, setting budgets for different expense categories, and in the future, analysing spending patterns over time. For the moment, the analysis can be done with software like Power BI connecting directly to the app database.

## Key Features
- Income and expense tracking with automatic categorization
- Budget setting and management
- Transaction import from various bank formats
- Manual review and modification of auto-categorized transactions
- Customizable transaction patterns for automatic categorization
- User-friendly interface with React frontend
- Database backup and restore functionality

## Quick Start
1. Clone the repository:
   ```
   git clone https://github.com/patogeno/family-budget-app.git
   cd family-budget-app
   ```

2. Set up the environment:
   - Create a `.env` file in the root directory (see [Configuration](docs/configuration.md) for details)
   - Install dependencies:
     ```
     pip install -r requirements.txt
     cd frontend && npm install && cd ..
     ```

3. Run the application:
   ```
   python manage.py runserver
   cd frontend && npm start
   ```

4. Visit `http://localhost:3000` in your browser to use the application.

## Database Backup and Restore

### Backing up the Database
To create a backup of your database, use the following command:

```
python manage.py backup_database
```

This will create a JSON file in the `database_backups` directory with a timestamp in the filename.

### Restoring the Database
To restore your database from a backup, use the following command:

```
python manage.py restore_database path/to/your/backup_file.json
```

Note: This process will flush your current database before restoring the backup. Make sure you have a backup of any important data before proceeding.

## API Documentation
To generate the API documentation, run the following command:

```
python manage.py generate_api_docs
```

This will create or update the `docs/api_documentation.md` file with the latest API documentation.

## Documentation
For more detailed information, please refer to the following documentation:

- [API Documentation](docs/api_documentation.md)
- [Import Formats](docs/import_formats.md)

More documentation coming soon:
- Getting Started
- User Guide
- Developer Guide
- Configuration
- Deployment
- Troubleshooting
- Contributing

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.