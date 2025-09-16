# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websitemypham', '0005_add_product_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_visible',
            field=models.BooleanField(default=True, verbose_name='Hiển thị trên website'),
        ),
    ]