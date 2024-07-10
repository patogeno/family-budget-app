from django import forms
from .models import AccountName, BudgetGroup, TransactionType
from django.conf import settings

class TransactionImportForm(forms.Form):
    IMPORT_FORMATS = [(k, v) for k, v in settings.BANK_FORMATS.items()]

    file = forms.FileField(label='Select a file')
    import_format = forms.ChoiceField(label='Import Format', choices=IMPORT_FORMATS)
    account_name = forms.ModelChoiceField(
        label='Account Name',
        queryset=AccountName.objects.all(),
        empty_label=None,
        required=False
    )
    new_account_name = forms.CharField(label='New Account Name', required=False)

class TransactionPatternImportForm(forms.Form):
    file = forms.FileField(label='Select a file')
    account_name = forms.ModelChoiceField(label='Account Name', queryset=AccountName.objects.all(), empty_label=None)

class AdjustmentTransactionForm(forms.Form):
    date_from = forms.DateField(label='Date From', widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(label='Date To', widget=forms.DateInput(attrs={'type': 'date'}))
    amount = forms.DecimalField(label='Amount', max_digits=10, decimal_places=2)
    budget_group = forms.ModelChoiceField(label='Budget Group', queryset=BudgetGroup.objects.all())
    transaction_type = forms.ModelChoiceField(label='Transaction Type', queryset=TransactionType.objects.all())
    description = forms.CharField(label='Description', max_length=255, initial='Date Adjustment', required=False)
    comments = forms.CharField(label='Comments', widget=forms.Textarea, required=False)