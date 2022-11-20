from rest_framework import serializers

import matricula.models as imm


class InscriptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = imm.Inscriptions
        exclude = ('created_at', 'updated_at')


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = imm.Course
        exclude = ('created_at', 'updated_at')


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = imm.Student
        exclude = ('created_at', 'updated_at', 'user')


class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = imm.Teacher
        exclude = ('created_at', 'updated_at', 'user')
