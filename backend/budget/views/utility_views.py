from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from ..models import Transaction, AccountName, TransactionType, BudgetGroup
from ..serializers import TransactionSerializer

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