# Generated by Django 3.2.5 on 2022-06-15 19:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('csvmaker', '0004_alter_column_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='type',
            field=models.CharField(choices=[('company', 'Company'), ('fullname', 'Full Name'), ('address', 'Address'), ('email', 'Email'), ('phone', 'Phone Number'), ('url', 'URL')], max_length=50),
        ),
        migrations.AlterField(
            model_name='schema',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
        ),
    ]
