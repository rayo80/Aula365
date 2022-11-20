from django.db import models
from users.models import CustomUser


# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    gender = models.CharField(max_length=50)
    address = models.TextField()
    edad = models.IntegerField()
    odigo = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Course(models.Model):
    name = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50)
    picture = models.TextField()
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE)
    horario = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Una inscripcion es la relacion de un alumno con un curso
class Inscriptions(models.Model):
    course = models.ForeignKey('Course', on_delete=models.DO_NOTHING, default=1)
    student = models.ForeignKey('Student', on_delete=models.DO_NOTHING, default=1)
    monto = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
