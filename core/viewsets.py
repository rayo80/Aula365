import datetime

from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet
from rest_framework.response import Response
from django.http import HttpRequest
from rest_framework import serializers, status
from rest_framework.settings import api_settings
from rest_framework import generics, mixins
from django.conf import settings


class SimpleSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class MyPagination(PageNumberPagination):
    page_size_query_param = 'size'  # items per page


def find_relations(model):
    select_related_fields = set()
    prefetch_related_fields = set()

    # noinspection PyProtectedMember
    for field in model._meta.get_fields():
        if field.many_to_many or field.one_to_many:
            prefetch_related_fields.add(field.name)

        elif field.one_to_one or field.many_to_one:
            select_related_fields.add(field.name)

    return select_related_fields, prefetch_related_fields


class DynamicFieldsMeta(type):

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        queryset = getattr(new_class, 'queryset')

        if queryset is not None:
            model = queryset.model
            new_class.select_related_fields, new_class.prefetch_related_fields = find_relations(model)

        return new_class


class HistoricalActionsMeta(DynamicFieldsMeta):
    """Generamos el serializer por defecto de la clase historical
    y lo agregamos como un atributo a la clase"""

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        queryset = getattr(new_class, 'queryset')

        if queryset is not None:
            if hasattr(queryset.model, 'historical'):
                class HistorySerializer(serializers.ModelSerializer):

                    class Meta:
                        model = queryset.model.history.model
                        fields = '__all__'
                new_class.history_serializer = HistorySerializer
            else:
                raise ValidationError("El modelo no posee tiene historical de atributo")
        return new_class


class MyGenericViewSet(GenericViewSet, metaclass=DynamicFieldsMeta):
    detail_serializer_class = None
    list_serializer_class = None
    prefetch_related = None
    select_related = None
    filters = []
    filter_required = False
    order = []
    http_method_names = ['get', 'put', 'post', 'delete']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom_query_fields = set()

    def get_query_fields(self):
        if hasattr(self.get_serializer_class().Meta, 'fields'):
            return self.get_serializer_class().Meta.fields
        elif hasattr(self.get_serializer_class().Meta, 'exclude'):
            return '__all__',
        # El caso exclude es momentaneo, funcionara pero no impedira,
        # que se ejecuten consultas innecesarias para el caso de los prefetch
        # related, e incluso para el caso de tener django admin habilitado,
        # se tumbara la peticion debido a la inacsesibilidad del field "logentry"

    def get_select_related(self):
        return self.select_related

    def get_prefetch_related(self):
        return self.prefetch_related

    def get_automatic_relateds(self):
        self.custom_query_fields.update(self.get_query_fields())

        if '__all__' not in self.custom_query_fields:
            select_related = self.select_related_fields & self.custom_query_fields
            prefetch_related = self.prefetch_related_fields & self.custom_query_fields

        else:
            prefetch_related = self.prefetch_related_fields
            print(prefetch_related)
            select_related = self.select_related_fields
        return select_related, prefetch_related

    def get_queryset(self):
        """jala automaticamente las anidaciones"""
        queryset = self.queryset
        select_related, prefetch_related = self.get_automatic_relateds()

        if self.get_select_related() is not None:
            select_related = self.get_select_related()

        if self.get_prefetch_related() is not None:
            prefetch_related = self.get_prefetch_related()
        print(prefetch_related)
        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        queryset = self.parse_filter(queryset)
        if self.order:
            queryset = queryset.order_by(*self.order)
        return queryset

    def get_serializer_class(self):
        if self.request and self.request.method == 'GET':
            if self.action == 'retrieve':
                if self.detail_serializer_class:
                    return self.detail_serializer_class
            else:
                if self.list_serializer_class:
                    return self.list_serializer_class
        return super().get_serializer_class()

    def parse_filter(self, queryset):
        filtro = self.get_filter(queryset)
        if filtro:
            print(filtro)
            queryset = queryset.filter(**filtro)
        else:
            if self.filter_required and self.action == 'list':
                raise ValidationError('Aplica algunos filtros')
            queryset = queryset.all()
        return queryset

    def get_filter(self, queryset):
        filtro = {}
        for f in self.filters:
            value_url = self.request.query_params.get(f)  # producto
            if value_url:
                if value_url == 'true':
                    filtro[f] = True
                if value_url == 'false':
                    filtro[f] = False
                if value_url == 'null':
                    filtro[f] = None
                else:
                    try:
                        filtro[f] = int(value_url)
                    except:
                        try:
                            filtro[f] = datetime.datetime.strptime(value_url, '%Y-%m-%d').date()
                        except ValueError:
                            raise ValidationError('El string tiene un formato invalido')

                """cuando no encuentra el campo en el request no debria hacer nada"""
        return filtro


class MyModelViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     MyGenericViewSet):
    pass


"""ADVANCE MODELVIEWSET"""


class AdvanceCreateModelMixin:
    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_create_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(self.get_create_response_serializer(instance).data,
                        status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        instance = serializer.save()
        return instance

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class AdvanceUpdateModelMixin:
    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_update_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance=self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(self.get_update_response_serializer(instance).data)

    def perform_update(self, serializer):
        instance = serializer.save()
        return instance

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class AdvanceGenericViewSet:
    """Genera Nuevos Metodos para funcionar con los nuevos Mixins"""
    create_serializer = None
    update_response_serializer = None
    update_serializer = None
    create_response_serializer = None
    read_serializer = None
    write_serializer = None

    def get_write_serializer(self):
        if self.write_serializer:
            return self.write_serializer
        else:
            return super().get_serializer_class()

    def get_read_serializer(self):
        if self.read_serializer:
            return self.read_serializer
        elif self.list_serializer_class:
            return self.list_serializer_class
        else:
            return super().get_serializer_class()

    def get_create_serialzer(self):
        if self.create_serializer:
            return self.create_serializer
        else:
            return self.get_write_serializer()

    def get_update_serializer(self):
        if self.update_serializer:
            return self.update_serializer
        else:
            return self.get_write_serializer()

    def get_update_response_serializer(self):
        if self.update_response_serializer:
            return self.update_response_serializer
        else:
            return self.get_read_serializer()

    def get_create_response_serializer(self):
        if self.create_response_serializer:
            return self.create_response_serializer
        else:
            return self.get_read_serializer()


class AdvanceViewSet(AdvanceUpdateModelMixin,
                     AdvanceCreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     AdvanceGenericViewSet,  # Nueva Funcionalidad
                     MyGenericViewSet,
                     ):
    pass
    """Reescribe las operaciones create and update
       Para tener un write serializer and Read Serializer"""


""" HISTORICAL VIEWSET """


class MyGenericHistoricalViewSet(MyGenericViewSet):
    historical_serializer = None
    user_serializer = None

    def get_historical_serializer(self):
        if self.historical_serializer:
            return self.historical_serializer
        serializer = self.get_default_historical()
        return serializer

    def get_user_serializer(self):
        if self.user_serializer:
            return self.user_serializer
        serializer = self.get_default_user_serializer()
        return serializer

    def get_default_user_serializer(self):
        class UserSerializer(serializers.ModelSerializer):
            class Meta:
                """Obtengo el usuario de mi aplicación"""
                model = settings.AUTH_USER_MODEL
                fields = '__all__'

        return UserSerializer

    def get_default_historical(self):
        class HistorySerializer(serializers.ModelSerializer):
            user = self.get_user_serializer()

            class Meta:
                model = self.queryset.model.history.model
                fields = '__all__'

        return HistorySerializer


class HistoricalModelMixin:
    """
     Generamos una accion en el viewset
    """

    @transaction.atomic(using='default')
    @action(detail=True)
    def history(self, request, pk=None):
        queryset = self.filter_queryset(self.get_queryset())
        history = queryset.model.historical.filter(id=pk).all()
        history_serializer = self.get_historical_serializer()
        serializer = history_serializer(history, many=True)
        return Response(serializer.data)


class MyHistoricalViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          mixins.DestroyModelMixin,
                          HistoricalModelMixin,
                          MyGenericHistoricalViewSet
                          ):
    pass


class AdvanceHistoricalViewSet(AdvanceUpdateModelMixin,
                               AdvanceCreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               HistoricalModelMixin,  # Action
                               AdvanceGenericViewSet,
                               MyGenericHistoricalViewSet
                               ):
    pass


def get_related(self, as_dict, query, key):
    if as_dict:
        return {q.id: q for q in query}
    else:
        return list(query)
