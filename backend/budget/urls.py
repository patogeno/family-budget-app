from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'account-names', views.AccountNameViewSet)
router.register(r'transaction-types', views.TransactionTypeViewSet)
router.register(r'transaction-patterns', views.TransactionPatternViewSet)
router.register(r'budget-groups', views.BudgetGroupViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'budget-initializations', views.BudgetInitializationViewSet)
router.register(r'budget-adjustments', views.BudgetAdjustmentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/import-transactions/', views.import_transactions, name='import_transactions'),
    path('api/import-transaction-patterns/', views.import_transaction_patterns, name='import_transaction_patterns'),
    path('api/create-adjustment-transaction/', views.create_adjustment_transaction, name='create_adjustment_transaction'),
    path('api/transactions/<int:transaction_id>/modify/', views.modify_transaction, name='modify_transaction'),
    path('api/bank-formats/', views.get_bank_formats, name='bank_formats'),
    path('api/paginated-transactions/', views.get_paginated_transactions, name='paginated_transactions'),
]