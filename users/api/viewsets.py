from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

import users.api.serializers as uss
from users.models import CustomUser


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = uss.UserSerializer
    queryset = CustomUser.objects
