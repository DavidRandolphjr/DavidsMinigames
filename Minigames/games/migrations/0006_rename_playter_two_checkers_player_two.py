# Generated by Django 4.1.7 on 2023-03-21 03:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_checkers_started_alter_checkers_team_owner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='checkers',
            old_name='playter_two',
            new_name='player_two',
        ),
    ]
