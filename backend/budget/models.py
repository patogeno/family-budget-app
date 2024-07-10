from django.db import models

class AccountName(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class TransactionType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    default_budget_group = models.ForeignKey('BudgetGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_transaction_types')
    amount_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    threshold_budget_group = models.ForeignKey('BudgetGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='threshold_transaction_types')

    def __str__(self):
        return self.name

class TransactionPattern(models.Model):
    regex_pattern = models.CharField(max_length=255)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    account_name = models.ForeignKey(AccountName, on_delete=models.CASCADE, null=True, blank=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.regex_pattern
    
    class Meta:
        unique_together = ('regex_pattern', 'account_name')

class BudgetGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    ASSIGNMENT_CHOICES = [
        ('manual', 'Manual'),
        ('auto_unchecked', 'Auto Unchecked'),
        ('auto_checked', 'Auto Checked'),
        ('unassigned', 'Unassigned'),
    ]

    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=100)
    account_name = models.ForeignKey(AccountName, on_delete=models.PROTECT)
    budget_group = models.ForeignKey(BudgetGroup, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.SET_NULL, null=True, blank=True)
    budget_group_assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_CHOICES)
    transaction_assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_CHOICES)
    review_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('confirmed', 'Confirmed'),
        ('modified', 'Modified'),
    ], default='pending')
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.description} - {self.amount}"

class BudgetInitialization(models.Model):
    budget_group = models.ForeignKey(BudgetGroup, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.budget_group.name} - {self.amount} - {self.date}"

class BudgetAdjustment(models.Model):
    from_budget_group = models.ForeignKey(BudgetGroup, on_delete=models.CASCADE, related_name='adjustments_from')
    to_budget_group = models.ForeignKey(BudgetGroup, on_delete=models.CASCADE, related_name='adjustments_to')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.from_budget_group.name} to {self.to_budget_group.name} - {self.amount} - {self.date}"
    
