from rest_framework import serializers

import matricula.models as mam
import core.fields as crf


class InscriptionsSerializer(serializers.ModelSerializer):
    student = crf.InstanceField(model=mam.Student)
    course = crf.InstanceField(model=mam.Course)

    class Meta:
        model = mam.Inscriptions
        exclude = ('created_at', 'updated_at')


class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = mam.Teacher
        exclude = ('created_at', 'updated_at', 'user')


class CourseSerializer(serializers.ModelSerializer):
    teacher = crf.InstanceField(model=mam.Teacher)

    class Meta:
        model = mam.Course
        exclude = ('created_at', 'updated_at')


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = mam.Student
        exclude = ('created_at', 'updated_at', 'user')

