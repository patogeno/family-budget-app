import re
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from .models import TransactionPattern, Transaction

def categorize_transaction(description, account_name, amount):
    patterns = TransactionPattern.objects.filter(account_name=account_name)
    for pattern in patterns:
        if re.search(pattern.regex_pattern, description, re.IGNORECASE):
            transaction_type = pattern.transaction_type
            budget_group = transaction_type.default_budget_group
            if transaction_type.amount_threshold and amount >= transaction_type.amount_threshold:
                budget_group = transaction_type.threshold_budget_group
            
            return transaction_type, budget_group, pattern.comments
    return None, None, None

def parse_transaction_data(reader, import_format):
    bank_formats = list(settings.BANK_FORMATS.keys())
    transaction_data = []

    if import_format == bank_formats[2]:
        next(reader)  # Skip the first row
        next(reader)  # Skip the second row

    for row in reader:
        if import_format in [bank_formats[0], bank_formats[1]]:
            transaction_date = datetime.strptime(row[0], '%d/%m/%Y').strftime('%Y-%m-%d')
            amount = row[1].replace('$', '').replace(',', '')
            description = row[2]
            balance = row[3].replace('$', '').replace(',', '') if import_format == bank_formats[0] else None
        elif import_format == bank_formats[2]:
            transaction_date = datetime.strptime(row[0], '%d/%m/%Y').strftime('%Y-%m-%d')
            description = row[1]
            amount = row[2].replace('$', '').replace(',', '')
            balance = row[3].replace('$', '').replace(',', '')
        else:
            raise ValueError(f"Unsupported import format: {import_format}")
        
        transaction_data.append({
            'date': transaction_date,
            'description': description,
            'amount': amount,
            'balance': balance,
        })

    return transaction_data

def detect_duplicates(transaction_data):
    unique_transactions = []
    transaction_counts = {}

    for transaction in transaction_data:
        # Create a tuple of the transaction details to use as a dictionary key
        transaction_key = (
            transaction['date'],
            transaction['description'],
            transaction['amount'],
            transaction['balance'],
        )

        if transaction_key in transaction_counts:
            transaction_counts[transaction_key] += 1
            # Only add counter for duplicates (count > 1)
            if transaction_counts[transaction_key] > 1:
                new_transaction = transaction.copy()
                new_transaction['description'] += f" ({transaction_counts[transaction_key]})"
                unique_transactions.append(new_transaction)
        else:
            transaction_counts[transaction_key] = 1
            unique_transactions.append(transaction)

    return unique_transactions