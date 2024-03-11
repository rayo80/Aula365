from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ValidationError
from rest_framework import fields

"""
class BaseField(fields.IntegerField):
    def __init__(self, relateds=None, *args, **kwargs):
        super().__init__(**kwargs)
        if relateds is None:
            relateds = []
        self.relateds = relateds

"""


class BaseRelatedsField(PrimaryKeyRelatedField):
    def __init__(self, relateds=None, *args, **kwargs):
        super().__init__(**kwargs)
        if relateds is None:
            relateds = []
        self.relateds = relateds

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        if hasattr(value, 'to_dict'):
            return value.to_dict()
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.pk)
        return value.pk

"""
class InstanceField(BaseField):
    def __init__(self, model=None, allow_inactive=True, *args, **kwargs):
        print("instanceField")
        super().__init__(**kwargs)
        self.model = model
        self.allow_inactive = allow_inactive

    def to_internal_value(self, data):
        if isinstance(data, self.model):
            return data
        data = super().to_internal_value(data)
        instance = self.model.objects.select_related(*self.relateds).filter(id=data).first()

        if instance is None:
            raise ValidationError(f"No existe {self.model.__name__} con el id enviado",
                                  code='does_not_exist')
        if self.allow_inactive is False:  # pasan solo los activos
            if hasattr(instance, 'activo') and instance.activo is False:
                raise ValidationError("El elemento enviado esta inactivo",
                                      code='inactive')
        return instance

    def to_representation(self, value):
        if hasattr(value, 'to_dict'):
            return value.to_dict()
        else:
            return value.pk
"""


class InstanceField(BaseRelatedsField):
    def __init__(self,  model=None, allow_inactive=True, *args, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.allow_inactive = allow_inactive

    def get_model(self):
        return self.model

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = self.model.objects
        self.queryset.select_related(*self.relateds)
        return self.queryset

    def to_internal_value(self, data):
        if isinstance(data, self.get_queryset().model):
            return data

        instance = super().to_internal_value(data)

        if self.allow_inactive is False:  # pasan solo los activos
            if hasattr(instance, 'activo') and instance.activo is False:
                raise ValidationError("El elemento enviado esta inactivo",
                                      code='inactive')
        return instance


class CustomChoiceField(fields.ChoiceField):

    def to_representation(self, value):
        if value:

            return {
                "id": value,
                "name": self._choices.get(value)
            }


class CurrencyField(fields.FloatField):

    def to_internal_value(self, data):
        return round(super().to_internal_value(data)*100)

    def to_representation(self, value):
        return value/100


class MonthField(fields.IntegerField):

    def to_internal_value(self, data):
        if data not in list(range(1, 13)):
            raise ValidationError('Mes no Valido', code='invalid')
        return data


class YearField(fields.IntegerField):

    def to_internal_value(self, data):
        if len(str(data)) != 4:
            raise ValidationError('El año debe contener 4 caracteres',
                                  code='invalid')
        return data
