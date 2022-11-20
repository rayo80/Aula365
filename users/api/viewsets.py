from rest_framework import viewsets
import users.api.serializers as uss


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = uss.UserSerializer
    queryset = uss.UserSerializer.Meta.model
