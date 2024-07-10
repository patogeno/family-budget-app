from rest_framework import serializers
from .models import AccountName, TransactionType, TransactionPattern, BudgetGroup, Transaction, BudgetInitialization, BudgetAdjustment

class AccountNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountName
        fields = ['id', 'name']

class TransactionTypeSerializer(serializers.ModelSerializer):
    default_budget_group = serializers.PrimaryKeyRelatedField(queryset=BudgetGroup.objects.all(), allow_null=True)
    threshold_budget_group = serializers.PrimaryKeyRelatedField(queryset=BudgetGroup.objects.all(), allow_null=True)

    class Meta:
        model = TransactionType
        fields = ['id', 'name', 'description', 'default_budget_group', 'amount_threshold', 'threshold_budget_group']

class TransactionPatternSerializer(serializers.ModelSerializer):
    transaction_type = serializers.PrimaryKeyRelatedField(queryset=TransactionType.objects.all())
    account_name = serializers.PrimaryKeyRelatedField(queryset=AccountName.objects.all(), allow_null=True)

    class Meta:
        model = TransactionPattern
        fields = ['id', 'regex_pattern', 'transaction_type', 'account_name', 'comments']

class BudgetGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetGroup
        fields = ['id', 'name', 'description']

class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.PrimaryKeyRelatedField(queryset=AccountName.objects.all())
    budget_group = serializers.PrimaryKeyRelatedField(queryset=BudgetGroup.objects.all(), allow_null=True)
    transaction_type = serializers.PrimaryKeyRelatedField(queryset=TransactionType.objects.all(), allow_null=True)

    class Meta:
        model = Transaction
        fields = ['id', 'date', 'amount', 'balance', 'description', 'source', 'account_name', 'budget_group', 
                  'transaction_type', 'budget_group_assignment_type', 'transaction_assignment_type', 
                  'review_status', 'comments']

class BudgetInitializationSerializer(serializers.ModelSerializer):
    budget_group = serializers.PrimaryKeyRelatedField(queryset=BudgetGroup.objects.all())

    class Meta:
        model = BudgetInitialization
        fields = ['id', 'budget_group', 'amount', 'date', 'description']

class BudgetAdjustmentSerializer(serializers.ModelSerializer):
    from_budget_group = serializers.PrimaryKeyRelatedField(queryset=BudgetGroup.objects.all())
    to_budget_group = serializers.PrimaryKeyRelatedField(queryset=BudgetGroup.objects.all())

    class Meta:
        model = BudgetAdjustment
        fields = ['id', 'from_budget_group', 'to_budget_group', 'amount', 'date', 'description']