from django.contrib import admin
from .models import TransactionType, TransactionPattern, BudgetGroup, Transaction, BudgetInitialization, BudgetAdjustment, AccountName
from datetime import date, timedelta

def set_type_budget(modeladmin, request, queryset, transaction_type, budget_group, comments=''):
    budget_group = BudgetGroup.objects.get(name=budget_group)
    transaction_type = TransactionType.objects.get(name=transaction_type)
    budget_group_assignment_type = 'manual'
    transaction_assignment_type = 'manual'
    review_status = 'modified'
    if comments:
        queryset.update(
            budget_group=budget_group,
            transaction_type=transaction_type,
            budget_group_assignment_type=budget_group_assignment_type,
            transaction_assignment_type=transaction_assignment_type,
            review_status=review_status,
            comments=comments
        )
    else:
        queryset.update(
            budget_group=budget_group,
            transaction_type=transaction_type,
            budget_group_assignment_type=budget_group_assignment_type,
            transaction_assignment_type=transaction_assignment_type,
            review_status=review_status
        )
    modeladmin.message_user(request, f"{queryset.count()} transactions were updated successfully.")

def set_to_income_savings(modeladmin, request, queryset):
    set_type_budget(modeladmin, request, queryset, 'Income', 'Savings')

set_to_income_savings.short_description = "Set to Income & Savings"

def set_to_home_savings(modeladmin, request, queryset):
    set_type_budget(modeladmin, request, queryset, 'Home', 'Savings')

set_to_home_savings.short_description = "Set to Home & Savings"

def set_to_holidays_holidays(modeladmin, request, queryset):
    set_type_budget(modeladmin, request, queryset, 'Holidays', 'Holidays')

set_to_holidays_holidays.short_description = "Set to Holidays & Holidays"

def set_to_transfer_disregard_pato(modeladmin, request, queryset):
    set_type_budget(modeladmin, request, queryset, 'Transfer', 'Disregard', 'Paid by Pato')

set_to_transfer_disregard_pato.short_description = "Set to Transfer & Disregard (Paid by Pato)"

# Action to confirm transactions auto assignment
def confirm_auto_assignment(modeladmin, request, queryset):
    # if assignment is manual, do not update
    queryset = queryset.filter(budget_group_assignment_type='auto_unchecked', transaction_assignment_type='auto_unchecked')
    queryset.update(
        budget_group_assignment_type='auto_checked',
        transaction_assignment_type='auto_checked',
        review_status='confirmed'
    )
    modeladmin.message_user(request, f"{queryset.count()} transactions were confirmed successfully.")

confirm_auto_assignment.short_description = "Confirm Auto Assignment"

# Function that recursively search budget adjustments until it founds a group of 3 or more adjustments in the same date that is a Monday
def find_last_fortnightly_adjustments(date):
    # Filter the budget adjustments on the date
    date_adjustments = BudgetAdjustment.objects.filter(date=date)
    
    # Check if there are any budget adjustments left before the date
    left_adjustments = BudgetAdjustment.objects.filter(date__lt=date).count()

    # If there are 3 or more adjustments, return the date
    if date_adjustments.exists() and date_adjustments.count() > 2 and date.weekday() == 0:
        return date
    elif not left_adjustments:
        return None
    else:
        # Calculate the previous fortnightly date
        if date.weekday() != 0:
            previous_fortnightly_date = date - timedelta(days=1)
        else:
            previous_fortnightly_date = date - timedelta(days=7)
        
        # Recursive call to find the last fortnightly adjustments
        return find_last_fortnightly_adjustments(previous_fortnightly_date)

def copy_last_fortnightly_adjustments(modeladmin, request, queryset):
    # Get the latest date from the existing budget adjustments which have more than 3 adjustments and it is a monday
    latest_date = find_last_fortnightly_adjustments(date.today())
    if latest_date is None:
        modeladmin.message_user(request, "No last fortnightly budget adjustments found.")
        return
    
    # Calculate the next fortnightly date
    next_fortnightly_date = latest_date + timedelta(days=14)
    
    # Filter the budget adjustments on the latest date
    latest_adjustments = BudgetAdjustment.objects.filter(date=latest_date)
    
    if latest_adjustments.exists():
        # Create new budget adjustments with the next fortnightly date
        new_adjustments = []
        for adjustment in latest_adjustments:
            new_adjustment = BudgetAdjustment(
                from_budget_group=adjustment.from_budget_group,
                to_budget_group=adjustment.to_budget_group,
                amount=adjustment.amount,
                date=next_fortnightly_date,
                description=adjustment.description
            )
            new_adjustments.append(new_adjustment)
        
        # Bulk create the new budget adjustments
        BudgetAdjustment.objects.bulk_create(new_adjustments)
        
        modeladmin.message_user(request, f"{len(new_adjustments)} budget adjustments were copied successfully.")
    else:
        modeladmin.message_user(request, "No budget adjustments found on the latest date.")

copy_last_fortnightly_adjustments.short_description = "Copy last fortnightly budget adjustments"

@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_budget_group')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(TransactionPattern)
class TransactionPatternAdmin(admin.ModelAdmin):
    list_display = ('regex_pattern', 'transaction_type', 'account_name')
    search_fields = ('regex_pattern',)
    list_filter = ('transaction_type', 'account_name')
    ordering = ('account_name', 'transaction_type', 'regex_pattern')

@admin.register(BudgetGroup)
class BudgetGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(AccountName)
class AccountNameAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('formatted_date', 'description', 'amount', 'balance', 'budget_group', 'transaction_type', 'account_name', 'comments', 'review_status')
    list_filter = ('date', 'budget_group', 'transaction_type', 'account_name', 'review_status')
    search_fields = ('description','amount','comments')
    date_hierarchy = 'date'
    actions = [set_to_income_savings, set_to_home_savings, set_to_holidays_holidays, set_to_transfer_disregard_pato, confirm_auto_assignment]
    ordering = ('-date', 'amount')

    def formatted_date(self, obj):
        return obj.date.strftime('%d/%m/%Y')
    formatted_date.short_description = 'Date'
    formatted_date.admin_order_field = 'date'

    def get_date_hierarchy_drilldown(self, year_lookup, month_lookup):
        from datetime import datetime
        from django.utils.formats import get_format

        date_format = get_format('DATE_FORMAT')
        date = datetime.strptime(f"{year_lookup}-{month_lookup}-01", "%Y-%m-%d")

        return {
            'date_hierarchy': self.date_hierarchy,
            'year_lookup': date.strftime('%Y'),
            'month_lookup': date.strftime('%m'),
            'day_lookup': None,
            'date_display': date.strftime(date_format),
        }

    def get_date_hierarchy_drilldown_regex(self, year_lookup, month_lookup):
        return r'^%s-%s-\d{2}$' % (year_lookup, month_lookup)

@admin.register(BudgetInitialization)
class BudgetInitializationAdmin(admin.ModelAdmin):
    list_display = ('budget_group', 'amount', 'date')
    list_filter = ('budget_group', 'date')
    ordering = ('date', 'budget_group')

@admin.register(BudgetAdjustment)
class BudgetAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('from_budget_group', 'to_budget_group', 'amount', 'date')
    list_filter = ('from_budget_group', 'to_budget_group', 'date')
    ordering = ('date', 'from_budget_group', 'to_budget_group')
    actions = [copy_last_fortnightly_adjustments]
