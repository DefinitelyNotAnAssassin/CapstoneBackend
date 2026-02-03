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
        migrations.CreateModel(
            name='LeaveCredit',
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
                ('year', models.IntegerField()),
                ('total_credits', models.DecimalField(decimal_places=2, max_digits=5)),
                ('used_credits', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('remaining_credits', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='leave_credits',
                    to='employees.employee',
                )),
            ],
            options={
                'verbose_name': 'Leave Credit',
                'verbose_name_plural': 'Leave Credits',
                'db_table': 'leave_management_leavecredit',
                'ordering': ['-year', 'leave_type'],
                'unique_together': {('employee', 'leave_type', 'year')},
            },
        ),
        migrations.CreateModel(
            name='LeaveBalance',
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
                ('current_balance', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('accrued_this_year', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('used_this_year', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('pending_requests', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='leave_balances',
                    to='employees.employee',
                )),
            ],
            options={
                'verbose_name': 'Leave Balance',
                'verbose_name_plural': 'Leave Balances',
                'db_table': 'leave_management_leavebalance',
                'ordering': ['employee', 'leave_type'],
                'unique_together': {('employee', 'leave_type')},
            },
        ),
    ]
