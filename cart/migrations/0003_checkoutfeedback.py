# cart/migrations/0003_checkoutfeedback.py
# Generated for adding CheckoutFeedback model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_item'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckoutFeedback',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('feedback_text', models.TextField(max_length=500)),
                ('date_submitted', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cart.order')),
            ],
        ),
    ]