from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.conf import settings
from decimal import Decimal
from datetime import datetime
import csv
import io
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import AccountName, TransactionType, TransactionPattern, BudgetGroup, Transaction, BudgetInitialization, BudgetAdjustment
from .serializers import AccountNameSerializer, TransactionTypeSerializer, TransactionPatternSerializer, BudgetGroupSerializer, TransactionSerializer, BudgetInitializationSerializer, BudgetAdjustmentSerializer
from .utils import categorize_transaction

class AccountNameViewSet(viewsets.ModelViewSet):
    queryset = AccountName.objects.all()
    serializer_class = AccountNameSerializer

class TransactionTypeViewSet(viewsets.ModelViewSet):
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer

class TransactionPatternViewSet(viewsets.ModelViewSet):
    queryset = TransactionPattern.objects.all()
    serializer_class = TransactionPatternSerializer

class BudgetGroupViewSet(viewsets.ModelViewSet):
    queryset = BudgetGroup.objects.all()
    serializer_class = BudgetGroupSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('date')
    serializer_class = TransactionSerializer

    @action(detail=False, methods=['get'])
    def pending_review(self, request):
        pending_transactions = self.queryset.filter(review_status='pending').order_by('date')
        serializer = self.get_serializer(pending_transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_confirm(self, request):
        transaction_ids = request.data.get('transaction_ids', [])
        comments_map = request.data.get('comments_map', {})

        transactions = Transaction.objects.filter(id__in=transaction_ids)
        for transaction in transactions:
            transaction.review_status = 'confirmed'
            transaction.transaction_assignment_type = 'auto_checked'
            transaction.budget_group_assignment_type = 'auto_checked'
            transaction.comments = comments_map.get(str(transaction.id), "")
            transaction.save()

        return Response({'message': 'Transactions confirmed successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def redo_categorization(self, request):
        uncategorized_transactions = Transaction.objects.filter(
            Q(transaction_assignment_type='auto_unchecked') | Q(transaction_assignment_type='unassigned') |
            Q(budget_group_assignment_type='auto_unchecked') | Q(budget_group_assignment_type='unassigned')
        )

        for transaction in uncategorized_transactions:
            transaction_type, budget_group, pattern_comments = categorize_transaction(transaction.description, transaction.account_name, transaction.amount)
            transaction.transaction_type = transaction_type
            transaction.budget_group = budget_group
            transaction.transaction_assignment_type = 'auto_unchecked' if transaction_type else 'unassigned'
            transaction.budget_group_assignment_type = 'auto_unchecked' if budget_group else 'unassigned'
            if not transaction.comments and pattern_comments:
                transaction.comments = pattern_comments
            transaction.save()

        serializer = self.get_serializer(uncategorized_transactions, many=True)
        return Response(serializer.data)

class BudgetInitializationViewSet(viewsets.ModelViewSet):
    queryset = BudgetInitialization.objects.all()
    serializer_class = BudgetInitializationSerializer

class BudgetAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = BudgetAdjustment.objects.all()
    serializer_class = BudgetAdjustmentSerializer

# Utility functions
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

# Custom API views
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
            print(transaction)
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

@api_view(['POST'])
def create_adjustment_transaction(request):
    date_from = request.data.get('date_from')
    date_to = request.data.get('date_to')
    amount = request.data.get('amount')
    budget_group_id = request.data.get('budget_group_id')
    transaction_type_id = request.data.get('transaction_type_id')
    description = request.data.get('description')
    comments = request.data.get('comments')
    
    account_name, _ = AccountName.objects.get_or_create(name='Adjustment Date')
    budget_group = BudgetGroup.objects.get(id=budget_group_id)
    transaction_type = TransactionType.objects.get(id=transaction_type_id)
    
    transaction_from = Transaction.objects.create(
        date=date_from,
        amount=float(amount),
        balance=None,
        description=description,
        source='manual_entry',
        account_name=account_name,
        budget_group=budget_group,
        transaction_type=transaction_type,
        budget_group_assignment_type='manual',
        transaction_assignment_type='manual',
        review_status='confirmed',
        comments=comments
    )
    
    transaction_to = Transaction.objects.create(
        date=date_to,
        amount=-float(amount),
        balance=None,
        description=description,
        source='manual_entry',
        account_name=account_name,
        budget_group=budget_group,
        transaction_type=transaction_type,
        budget_group_assignment_type='manual',
        transaction_assignment_type='manual',
        review_status='confirmed',
        comments=comments
    )
    
    return Response({'message': 'Adjustment transactions created successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def modify_transaction(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return Response({'success': False, 'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

    # Update fields
    if 'transaction_type' in request.data:
        transaction.transaction_type_id = request.data['transaction_type']
    if 'budget_group' in request.data:
        transaction.budget_group_id = request.data['budget_group']
    if 'comments' in request.data:
        transaction.comments = request.data['comments']
    if 'review_status' in request.data:
        transaction.review_status = request.data['review_status']
    
    transaction.transaction_assignment_type = 'manual'
    transaction.budget_group_assignment_type = 'manual'
    if transaction.review_status != 'confirmed':
        transaction.review_status = 'modified'
    
    transaction.save()
    
    return Response({'success': True, 'message': 'Transaction updated successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_bank_formats(request):
    return Response(settings.BANK_FORMATS)

@api_view(['GET'])
def get_paginated_transactions(request):
    # Get query parameters
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 10)
    sort_by = request.GET.get('sort_by', 'date')
    sort_direction = request.GET.get('sort_direction', 'desc')
    
    # Get filter parameters
    date_from = request.GET.get('dateFrom')
    date_to = request.GET.get('dateTo')
    description = request.GET.get('description')
    transaction_type = request.GET.get('type')
    budget_group = request.GET.get('budget')
    account = request.GET.get('account')
    review_status = request.GET.get('review_status')

    # Start with all transactions
    transactions = Transaction.objects.all()

    # Apply filters
    if date_from:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        transactions = transactions.filter(date__lte=date_to)
    if description:
        transactions = transactions.filter(description__icontains=description)
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if budget_group:
        transactions = transactions.filter(budget_group=budget_group)
    if account:
        transactions = transactions.filter(account_name=account)
    if review_status:
        transactions = transactions.filter(review_status=review_status)

    # Apply sorting
    sort_prefix = '-' if sort_direction == 'desc' else ''
    transactions = transactions.order_by(f'{sort_prefix}{sort_by}')

    # Paginate results
    paginator = Paginator(transactions, per_page)
    try:
        paginated_transactions = paginator.page(page)
    except PageNotAnInteger:
        paginated_transactions = paginator.page(1)
    except EmptyPage:
        paginated_transactions = paginator.page(paginator.num_pages)

    # Serialize data
    serializer = TransactionSerializer(paginated_transactions, many=True)

    return Response({
        'transactions': serializer.data,
        'total_pages': paginator.num_pages,
        'current_page': int(page),
        'total_transactions': paginator.count
    })