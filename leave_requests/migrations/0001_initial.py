# Generated migration that uses existing leave_management tables
# No operations needed since db_table is set in the model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveRequest',
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
                )),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('days_requested', models.IntegerField()),
                ('reason', models.TextField()),
                ('status', models.CharField(
                    choices=[
                        ('Pending', 'Pending'),
                        ('Approved', 'Approved'),
                        ('Rejected', 'Rejected'),
                        ('Cancelled', 'Cancelled'),
                    ],
                    default='Pending',
                    max_length=20,
                )),
                ('approval_date', models.DateTimeField(blank=True, null=True)),
                ('approval_notes', models.TextField(blank=True, null=True)),
                ('supporting_documents', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='approved_leaves',
                    to='employees.employee',
                )),
                ('employee', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='leave_requests',
                    to='employees.employee',
                )),
            ],
            options={
                'verbose_name': 'Leave Request',
                'verbose_name_plural': 'Leave Requests',
                'db_table': 'leave_management_leaverequest',
                'ordering': ['-created_at'],
            },
        ),
    ]
