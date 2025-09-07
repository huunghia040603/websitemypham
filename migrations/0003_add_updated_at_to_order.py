# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BuddyApp', '0002_add_shipping_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật'),
        ),
    ]