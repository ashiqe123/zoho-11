# Generated by Django 4.2.1 on 2023-07-12 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zohoapp', '0023_purchase_order_org_state_purchase_order_org_street_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase_order',
            name='Org_city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='purchase_order',
            name='customer_city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
