import re
from .models import TransactionPattern

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