# Generated by Django 4.2.2 on 2023-06-25 13:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_table_p1_alter_table_p2_alter_table_p3_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='uid',
            field=models.UUIDField(default=uuid.UUID('f97742a4-4bdf-4a44-b6e8-416603346994')),
        ),
    ]
