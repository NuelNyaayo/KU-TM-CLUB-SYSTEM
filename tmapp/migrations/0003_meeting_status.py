# Generated by Django 5.1.6 on 2025-03-25 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmapp', '0002_customuser_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='status',
            field=models.CharField(choices=[('Upcoming', 'Upcoming Meeting'), ('Ongoing', 'Ongoing Meeting'), ('Previous', 'Previous Meeting')], default='Upcoming', max_length=10),
        ),
    ]
