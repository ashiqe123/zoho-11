# Generated by Django 3.2.18 on 2023-07-01 08:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zohoapp', '0015_auto_20230630_1328'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_name', models.CharField(max_length=255)),
                ('comment', models.CharField(max_length=255)),
                ('expense', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zohoapp.expense')),
            ],
        ),
    ]