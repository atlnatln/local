from rest_framework import viewsets, permissions
from .models import Record, RecordField
from .serializers import RecordSerializer, RecordFieldSerializer

class RecordViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['firm_name', 'firm_id']
    ordering_fields = ['firm_name', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Record.objects.none()
        
        # Filter records belonging to batches of organizations the user is a member of
        # Note: This assumes correct reverse relationship names. 
        # Check OrganizationMember related_name for user.
        return Record.objects.filter(
            batch__organization__members__user=user
        ).distinct()

class RecordFieldViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RecordFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
         user = self.request.user
         if not user.is_authenticated:
            return RecordField.objects.none()
         
         return RecordField.objects.filter(
             record__batch__organization__members__user=user
         ).distinct()
