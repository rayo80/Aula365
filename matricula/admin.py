from django.contrib import admin
from matricula.models import Teacher, Student, Inscriptions, Course

# Register your models here.
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Inscriptions)
admin.site.register(Course)
