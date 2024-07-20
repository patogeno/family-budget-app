from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import transaction_views, import_views, review_views, utility_views

router = DefaultRouter()
router.register(r'account-names', transaction_views.AccountNameViewSet, basename='account-name')
router.register(r'transaction-types', transaction_views.TransactionTypeViewSet, basename='transaction-type')
router.register(r'transaction-patterns', transaction_views.TransactionPatternViewSet, basename='transaction-pattern')
router.register(r'budget-groups', transaction_views.BudgetGroupViewSet, basename='budget-group')
router.register(r'budget-initializations', transaction_views.BudgetInitializationViewSet, basename='budget-initialization')
router.register(r'budget-adjustments', transaction_views.BudgetAdjustmentViewSet, basename='budget-adjustment')
router.register(r'transactions', transaction_views.TransactionViewSet, basename='transaction')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/import-transactions/', import_views.import_transactions, name='import-transactions'),
    path('api/import-transaction-patterns/', import_views.import_transaction_patterns, name='import-transaction-patterns'),
    path('api/transactions/<int:transaction_id>/modify/', review_views.modify_transaction, name='modify-transaction'),
    path('api/bank-formats/', utility_views.get_bank_formats, name='bank-formats'),
    path('api/paginated-transactions/', utility_views.get_paginated_transactions, name='paginated-transactions'),
    path('api/create-adjustment-transaction/', transaction_views.create_adjustment_transaction, name='create-adjustment-transaction'),
]