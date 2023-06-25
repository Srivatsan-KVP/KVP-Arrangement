# Generated by Django 4.2.2 on 2023-06-24 13:11

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_teacher_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='uid',
            field=models.UUIDField(default=uuid.UUID('7dee52fc-9188-4197-94a3-29e350fd9697'), unique=True),
        ),
        migrations.CreateModel(
            name='Absent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.teacher')),
            ],
        ),
    ]