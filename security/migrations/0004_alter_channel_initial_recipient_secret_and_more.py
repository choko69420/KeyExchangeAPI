# Generated by Django 5.0.6 on 2024-06-16 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0003_alter_channel_initial_recipient_secret_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='initial_recipient_secret',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='channel',
            name='initial_sender_secret',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
