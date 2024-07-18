from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.conf import settings
from decimal import Decimal
from datetime import datetime
import csv
import io
from ..models import Transaction, AccountName, TransactionPattern, TransactionType, BudgetGroup
from ..serializers import TransactionSerializer
from ..utils import categorize_transaction, parse_transaction_data, detect_duplicates

@api_view(['POST'])
def import_transactions(request):
    file = request.FILES.get('file')
    import_format = request.data.get('import_format')
    account_name_id = request.data.get('account_name')
    new_account_name = request.data.get('new_account_name')

    if not file:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    if import_format not in settings.BANK_FORMATS.keys():
        return Response({'error': 'Import format not specified'}, status=status.HTTP_400_BAD_REQUEST)

    if new_account_name:
        account_name, _ = AccountName.objects.get_or_create(name=new_account_name)
    elif account_name_id:
        account_name = AccountName.objects.get(id=account_name_id)
    else:
        return Response({'error': 'Account name not provided'}, status=status.HTTP_400_BAD_REQUEST)

    csv_file = io.StringIO(file.read().decode('utf-8-sig'))
    reader = csv.reader(csv_file)

    transaction_data = parse_transaction_data(reader, import_format)
    unique_transactions = detect_duplicates(transaction_data)

    for transaction in unique_transactions:
        duplicate_exists = Transaction.objects.filter(
            Q(date=transaction['date']) &
            Q(description=transaction['description']) &
            Q(amount=transaction['amount']) &
            Q(account_name_id=account_name.id) &
            Q(balance=transaction['balance'])
        ).exists()

        if not duplicate_exists:
            transaction_type, budget_group, pattern_comments = categorize_transaction(transaction['description'], account_name, Decimal(transaction['amount']))
            transaction_assignment_type = 'auto_unchecked' if transaction_type else 'unassigned'
            budget_group_assignment_type = 'auto_unchecked' if budget_group else 'unassigned'
            
            serializer = TransactionSerializer(data={
                **transaction,
                'source': import_format,
                'account_name': account_name.id,
                'transaction_type': transaction_type.id if transaction_type else None,
                'budget_group': budget_group.id if budget_group else None,
                'transaction_assignment_type': transaction_assignment_type,
                'budget_group_assignment_type': budget_group_assignment_type,
                'comments': pattern_comments
            })
            
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Transactions imported successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def import_transaction_patterns(request):
    file = request.FILES.get('file')
    account_name_id = request.data.get('account_name')

    if not file:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    if not account_name_id:
        return Response({'error': 'Account name not provided'}, status=status.HTTP_400_BAD_REQUEST)

    account_name = AccountName.objects.get(id=account_name_id)

    csv_file = io.StringIO(file.read().decode('utf-8-sig'))
    reader = csv.DictReader(csv_file)

    for row in reader:
        regex_pattern = row['Pattern']
        transaction_type_name = row['Category']
        comments = row['Comments']
        
        transaction_type, _ = TransactionType.objects.get_or_create(name=transaction_type_name)

        transaction_pattern, created = TransactionPattern.objects.update_or_create(
            regex_pattern=regex_pattern,
            account_name=account_name,
            defaults={
                'transaction_type': transaction_type,
                'comments': comments
            }
        )

    return Response({'message': 'Transaction patterns imported successfully'}, status=status.HTTP_201_CREATED)