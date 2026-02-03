# Generated migration that uses existing leave_management tables
# No operations needed since db_table is set in the model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0002_initial'),
        ('leave_requests', '0001_initial'),
    ]

    operations = [
         ]
