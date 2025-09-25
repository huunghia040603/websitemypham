# Generated manually to fix base64 URL length issue

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BuddyApp', '0006_add_is_visible_to_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ctvapplication',
            name='cccd_back_url',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='ctvapplication',
            name='cccd_front_url',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='ctv',
            name='cccd_back_url',
            field=models.TextField(blank=True, null=True, verbose_name='Ảnh CCCD mặt sau'),
        ),
        migrations.AlterField(
            model_name='ctv',
            name='cccd_front_url',
            field=models.TextField(blank=True, null=True, verbose_name='Ảnh CCCD mặt trước'),
        ),
    ]