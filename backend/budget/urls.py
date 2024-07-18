from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import transaction_views, import_views, review_views, utility_views

router = DefaultRouter()
router.register(r'account-names', transaction_views.AccountNameViewSet)
router.register(r'transaction-types', transaction_views.TransactionTypeViewSet)
router.register(r'transaction-patterns', transaction_views.TransactionPatternViewSet)
router.register(r'budget-groups', transaction_views.BudgetGroupViewSet)
router.register(r'budget-initializations', transaction_views.BudgetInitializationViewSet)
router.register(r'budget-adjustments', transaction_views.BudgetAdjustmentViewSet)
router.register(r'transactions', transaction_views.TransactionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/import-transactions/', import_views.import_transactions, name='import_transactions'),
    path('api/import-transaction-patterns/', import_views.import_transaction_patterns, name='import_transaction_patterns'),
    path('api/transactions/<int:transaction_id>/modify/', review_views.modify_transaction, name='modify_transaction'),
    path('api/bank-formats/', utility_views.get_bank_formats, name='bank_formats'),
    path('api/paginated-transactions/', utility_views.get_paginated_transactions, name='paginated_transactions'),
    path('api/create-adjustment-transaction/', transaction_views.create_adjustment_transaction, name='create_adjustment_transaction'),
]