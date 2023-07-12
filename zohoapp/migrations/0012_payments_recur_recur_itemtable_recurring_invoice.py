# Generated by Django 3.2.18 on 2023-06-27 06:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zohoapp', '0011_challanitems_deliverychellan'),
    ]

    operations = [
        migrations.CreateModel(
            name='payments_recur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Terms', models.CharField(blank=True, max_length=100, null=True)),
                ('Days', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='recurring_invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cname', models.CharField(max_length=255)),
                ('p_supply', models.CharField(max_length=255)),
                ('entry_type', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('order_num', models.CharField(max_length=255)),
                ('every', models.CharField(max_length=255)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('terms', models.CharField(max_length=255)),
                ('cust_note', models.TextField()),
                ('conditions', models.TextField()),
                ('sub_total', models.FloatField(blank=True, null=True)),
                ('igst', models.FloatField(blank=True, null=True)),
                ('sgst', models.FloatField(blank=True, null=True)),
                ('cgst', models.FloatField(blank=True, null=True)),
                ('tax_amount', models.FloatField(blank=True, null=True)),
                ('shipping_charge', models.FloatField(blank=True, null=True)),
                ('adjustment', models.FloatField(blank=True, null=True)),
                ('total', models.FloatField(blank=True, null=True)),
                ('cust_name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='zohoapp.customer')),
                ('items', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='zohoapp.additem')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='recur_itemtable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iname', models.CharField(max_length=255)),
                ('quantity', models.FloatField(blank=True, null=True)),
                ('rate', models.FloatField(blank=True, null=True)),
                ('discount', models.FloatField(blank=True, null=True)),
                ('tax', models.FloatField(blank=True, null=True)),
                ('amt', models.FloatField(blank=True, null=True)),
                ('ri', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='zohoapp.recurring_invoice')),
            ],
        ),
    ]