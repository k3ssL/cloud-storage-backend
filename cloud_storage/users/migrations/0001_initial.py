# Generated by Django 5.0.2 on 2024-02-20 17:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=256, validators=[django.core.validators.MinLengthValidator(3, message='Пароль слишком короткий'), django.core.validators.RegexValidator(message='Пароль должен содержать одну строчку букву, одну заглавную и одну цифру', regex='^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)')])),
                ('first_name', models.CharField(blank=True, max_length=254)),
                ('last_name', models.CharField(blank=True, max_length=254)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
