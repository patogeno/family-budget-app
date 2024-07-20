from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from ..models import Transaction, AccountName, TransactionType, BudgetGroup
from ..serializers import TransactionSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    operation_description="Get all available bank formats",
    responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        additional_properties=openapi.Schema(type=openapi.TYPE_STRING),
        description="A dictionary of bank format keys and their descriptions"
    )}
)
@api_view(['GET'])
def get_bank_formats(request):
    """
    Retrieve all available bank formats.

    This endpoint returns a dictionary of bank format keys and their descriptions,
    as defined in the project settings.

    Returns:
    - 200 OK with a dictionary of bank formats
    """
    return Response(settings.BANK_FORMATS)

@swagger_auto_schema(
    method='get',
    operation_description="Get paginated and filtered transactions",
    manual_parameters=[
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        openapi.Parameter('per_page', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
        openapi.Parameter('sort_by', openapi.IN_QUERY, description="Field to sort by", type=openapi.TYPE_STRING),
        openapi.Parameter('sort_direction', openapi.IN_QUERY, description="Sort direction (asc or desc)", type=openapi.TYPE_STRING),
        openapi.Parameter('dateFrom', openapi.IN_QUERY, description="Start date for filtering (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        openapi.Parameter('dateTo', openapi.IN_QUERY, description="End date for filtering (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        openapi.Parameter('description', openapi.IN_QUERY, description="Filter by description", type=openapi.TYPE_STRING),
        openapi.Parameter('type', openapi.IN_QUERY, description="Filter by transaction type ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('budget', openapi.IN_QUERY, description="Filter by budget group ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('account', openapi.IN_QUERY, description="Filter by account ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('review_status', openapi.IN_QUERY, description="Filter by review status", type=openapi.TYPE_STRING),
    ],
    responses={200: openapi.Response(
        description="Successful response",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'transactions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                            'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                            'balance': openapi.Schema(type=openapi.TYPE_NUMBER),
                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                            'source': openapi.Schema(type=openapi.TYPE_STRING),
                            'account_name': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'budget_group': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'transaction_type': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'budget_group_assignment_type': openapi.Schema(type=openapi.TYPE_STRING),
                            'transaction_assignment_type': openapi.Schema(type=openapi.TYPE_STRING),
                            'review_status': openapi.Schema(type=openapi.TYPE_STRING),
                            'comments': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                ),
                'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                'current_page': openapi.Schema(type=openapi.TYPE_INTEGER),
                'total_transactions': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    )}
)
@api_view(['GET'])
def get_paginated_transactions(request):
    """
    Retrieve a paginated and filtered list of transactions.

    This endpoint allows for pagination, sorting, and filtering of transactions based on various criteria.

    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Number of items per page (default: 10)
    - sort_by: Field to sort by (default: 'date')
    - sort_direction: Sort direction, 'asc' or 'desc' (default: 'desc')
    - dateFrom: Start date for filtering (format: YYYY-MM-DD)
    - dateTo: End date for filtering (format: YYYY-MM-DD)
    - description: Filter by description (case-insensitive partial match)
    - type: Filter by transaction type ID
    - budget: Filter by budget group ID
    - account: Filter by account ID
    - review_status: Filter by review status

    Returns:
    - 200 OK with paginated transactions, total pages, current page, and total transaction count
    """
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