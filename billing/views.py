from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, mixins, filters
from .models import Bill, Transaction
from .serializers import UserSerializer, BillSerializer, TransactionSerializer


class UserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    владелец счета
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny, )


class BillViewSet(viewsets.ReadOnlyModelViewSet):
    """
    состояние счетов
    """
    serializer_class = BillSerializer
    queryset = Bill.objects.all()
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


class TransactionInViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    """
    входящие переводы
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['source_bill__owner__username']
    ordering_fields = '__all__'
    ordering = 'pk'
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return self.queryset.filter(dest_bill__owner=self.request.user)


class TransactionOutViewSet(mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    """
    исходящие переводы
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['dest_bill__owner__username']
    ordering_fields = '__all__'
    ordering = 'pk'
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return self.queryset.filter(source_bill__owner=self.request.user)
