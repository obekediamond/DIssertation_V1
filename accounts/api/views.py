from rest_framework import generics
from django.contrib.auth.views import get_user_model

from .serializers import UserSerializer

User = get_user_model()


class UserListAPIView(generics.ListAPIView):
    lookup_field = 'id'
    serializer_class = UserSerializer

    def get_queryset(self):
        query_set = User.objects.all()
        query = self.request.GET.get('q')
        if query is not None:
            query_set = query_set.filter(username__iexact=query)
        return query_set


class UserDetailView(generics.RetrieveAPIView):
    lookup_field = 'id'
    queryset = User.objects.all()
    model = User
