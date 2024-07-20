from rest_framework.decorators import api_view
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from ..models import Transaction, AccountName, TransactionType, TransactionPattern, BudgetGroup, BudgetInitialization, BudgetAdjustment
from ..serializers import TransactionSerializer, AccountNameSerializer, TransactionTypeSerializer, TransactionPatternSerializer, BudgetGroupSerializer, BudgetInitializationSerializer, BudgetAdjustmentSerializer
from ..utils import categorize_transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class AccountNameViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows account names to be viewed or edited.
    """
    queryset = AccountName.objects.all()
    serializer_class = AccountNameSerializer

class TransactionTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows transaction types to be viewed or edited.
    """
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer

class TransactionPatternViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows transaction patterns to be viewed or edited.
    """
    queryset = TransactionPattern.objects.all()
    serializer_class = TransactionPatternSerializer

class BudgetGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows budget groups to be viewed or edited.
    """
    queryset = BudgetGroup.objects.all()
    serializer_class = BudgetGroupSerializer

class BudgetInitializationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows budget initializations to be viewed or edited.
    """
    queryset = BudgetInitialization.objects.all()
    serializer_class = BudgetInitializationSerializer

class BudgetAdjustmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows budget adjustments to be viewed or edited.
    """
    queryset = BudgetAdjustment.objects.all()
    serializer_class = BudgetAdjustmentSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows transactions to be viewed or edited.
    """
    queryset = Transaction.objects.all().order_by('date')
    serializer_class = TransactionSerializer

    @swagger_auto_schema(
        operation_description="List transactions pending review",
        responses={200: TransactionSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def pending_review(self, request):
        """
        Retrieve a list of transactions pending review.
        """
        pending_transactions = self.queryset.filter(review_status='pending').order_by('date')
        serializer = self.get_serializer(pending_transactions, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Confirm multiple transactions",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'transaction_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
                'comments_map': openapi.Schema(type=openapi.TYPE_OBJECT, additionalProperties=openapi.Schema(type=openapi.TYPE_STRING))
            },
            required=['transaction_ids']
        ),
        responses={200: openapi.Response(description="Transactions confirmed successfully")}
    )
    @action(detail=False, methods=['post'])
    def bulk_confirm(self, request):
        """
        Confirm multiple transactions in bulk.
        """
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

    @swagger_auto_schema(
        operation_description="Redo categorization for uncategorized transactions",
        responses={200: TransactionSerializer(many=True)}
    )
    @action(detail=False, methods=['post'])
    def redo_categorization(self, request):
        """
        Redo categorization for uncategorized transactions.
        """
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

@swagger_auto_schema(
    method='post',
    operation_description="Create an adjustment transaction",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'date_from': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            'date_to': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
            'budget_group_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'transaction_type_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'description': openapi.Schema(type=openapi.TYPE_STRING),
            'comments': openapi.Schema(type=openapi.TYPE_STRING)
        },
        required=['date_from', 'date_to', 'amount', 'budget_group_id', 'transaction_type_id']
    ),
    responses={201: openapi.Response(description="Adjustment transactions created successfully")}
)
@api_view(['POST'])
def create_adjustment_transaction(request):
    """
    Create an adjustment transaction.
    """
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