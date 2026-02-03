# Generated migration that uses existing leave_management tables
# No operations needed since db_table is set in the model

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='LeavePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_type', models.CharField(
                    choices=[
                        ('Vacation Leave', 'Vacation Leave'),
                        ('Sick Leave', 'Sick Leave'),
                        ('Birthday Leave', 'Birthday Leave'),
                        ('Solo Parent Leave', 'Solo Parent Leave'),
                        ('Bereavement Leave', 'Bereavement Leave'),
                        ('Paternity Leave', 'Paternity Leave'),
                        ('Maternity Leave', 'Maternity Leave'),
                    ],
                    max_length=50,
                    unique=True,
                )),
                ('days_allowed', models.IntegerField()),
                ('description', models.TextField()),
                ('requires_approval', models.BooleanField(default=True)),
                ('requires_documentation', models.BooleanField(default=False)),
                ('applicable_positions', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Leave Policy',
                'verbose_name_plural': 'Leave Policies',
                'db_table': 'leave_management_leavepolicy',
                'ordering': ['leave_type'],
            },
        ),
    ]
