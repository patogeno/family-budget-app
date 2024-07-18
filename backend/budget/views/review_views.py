from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Transaction

@api_view(['POST'])
def modify_transaction(request, transaction_id):
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