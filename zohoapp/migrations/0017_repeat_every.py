# Generated by Django 3.2.18 on 2023-07-01 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zohoapp', '0016_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='repeat_every',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Terms', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
