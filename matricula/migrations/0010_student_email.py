# Generated by Django 4.1.2 on 2022-12-08 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0009_alter_course_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='email',
            field=models.EmailField(default='nmame@dfsf', max_length=254),
            preserve_default=False,
        ),
    ]
