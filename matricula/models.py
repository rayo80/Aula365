from django.db import models
from users.models import CustomUser


# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    gender = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=50)
    email = models.EmailField()
    edad = models.IntegerField()
    codigo = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_dict(self):
        print("no llego")
        return {
            "id": self.id,
            "name": self.name
        }


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50)
    formacion = models.CharField(max_length=255)
    picture = models.TextField(null=False)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_dict(self):
        print("no llego")
        return {
            "id": self.id,
            "name": self.name
        }


class Course(models.Model):
    name = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50)
    picture = models.TextField(null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    horario = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


# Una inscripcion es la relacion de un alumno con un curso
class Inscriptions(models.Model):
    course = models.ForeignKey('Course', on_delete=models.DO_NOTHING, null=False)
    student = models.ForeignKey('Student', on_delete=models.DO_NOTHING, null=False)
    fecha = models.DateField()
    monto = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
