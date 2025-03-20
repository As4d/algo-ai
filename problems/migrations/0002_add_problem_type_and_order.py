from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='problem_type',
            field=models.CharField(
                choices=[
                    ('problem_set', 'Problem Set'),
                    ('python_basics', 'Python Basics'),
                    ('cpp_basics', 'C++ Basics'),
                    ('numpy', 'NumPy'),
                ],
                default='problem_set',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='problem',
            name='order',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterModelOptions(
            name='problem',
            options={'ordering': ['order', 'created_at']},
        ),
    ] 