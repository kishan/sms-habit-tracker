# Generated by Django 4.0.5 on 2022-12-18 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habit_tracker', '0004_alter_journalentry_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalentry',
            name='master_summary',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='summary1',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='summary2',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='summary3',
            field=models.TextField(default=''),
        ),
    ]