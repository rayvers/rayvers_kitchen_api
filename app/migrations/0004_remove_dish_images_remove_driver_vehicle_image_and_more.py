# Generated by Django 4.2.9 on 2025-03-02 02:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_dish_delivery_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dish',
            name='images',
        ),
        migrations.RemoveField(
            model_name='driver',
            name='vehicle_image',
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='image',
        ),
        migrations.DeleteModel(
            name='Image',
        ),
    ]
