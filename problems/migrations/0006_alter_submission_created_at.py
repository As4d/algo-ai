# Generated by Django 5.1.4 on 2025-05-01 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0005_alter_problem_test_cases'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
