from rest_framework.decorators import api_view
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from ..models import Transaction, AccountName, TransactionType, TransactionPattern, BudgetGroup, BudgetInitialization, BudgetAdjustment
from ..serializers import TransactionSerializer, AccountNameSerializer, TransactionTypeSerializer, TransactionPatternSerializer, BudgetGroupSerializer, BudgetInitializationSerializer, BudgetAdjustmentSerializer
from ..utils import categorize_transaction

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

class BudgetInitializationViewSet(viewsets.ModelViewSet):
    queryset = BudgetInitialization.objects.all()
    serializer_class = BudgetInitializationSerializer

class BudgetAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = BudgetAdjustment.objects.all()
    serializer_class = BudgetAdjustmentSerializer

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