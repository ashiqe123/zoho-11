# Generated by Django 4.2.1 on 2023-07-14 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zohoapp', '0024_purchase_order_org_city_purchase_order_customer_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase_order',
            name='Org_mail',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
