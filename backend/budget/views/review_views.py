from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_description="Modify a specific transaction",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'transaction_type': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the transaction type"),
            'budget_group': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the budget group"),
            'comments': openapi.Schema(type=openapi.TYPE_STRING, description="Additional comments for the transaction"),
            'review_status': openapi.Schema(type=openapi.TYPE_STRING, enum=['pending', 'confirmed', 'modified'], description="Review status of the transaction")
        }
    ),
    responses={
        200: openapi.Response(
            description="Transaction updated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        404: openapi.Response(description="Transaction not found")
    }
)
@api_view(['POST'])
def modify_transaction(request, transaction_id):
    """
    Modify a specific transaction.

    This view allows updating various fields of a transaction, including its type,
    budget group, comments, and review status. It's primarily used in the review
    process to categorize and confirm transactions.

    Parameters:
    - transaction_id: The ID of the transaction to modify

    Request body can include:
    - transaction_type: ID of the new transaction type
    - budget_group: ID of the new budget group
    - comments: New or updated comments for the transaction
    - review_status: New review status ('pending', 'confirmed', or 'modified')

    Returns:
    - 200 OK with a success message if the transaction is updated successfully
    - 404 Not Found if the transaction doesn't exist
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return Response({'success': False, 'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

    # Update fields
    if 'transaction_type' in request.data:
        transaction.transaction_type_id = request.data['transaction_type']
    if 'budget_group' in request.data:
        transaction.budget_group_id = request.data['budget_group']
    if 'comments' in request.data:
        transaction.comments = request.data['comments']
    if 'review_status' in request.data:
        transaction.review_status = request.data['review_status']
    
    transaction.transaction_assignment_type = 'manual'
    transaction.budget_group_assignment_type = 'manual'
    if transaction.review_status != 'confirmed':
        transaction.review_status = 'modified'
    
    transaction.save()
    
    return Response({'success': True, 'message': 'Transaction updated successfully'}, status=status.HTTP_200_OK)