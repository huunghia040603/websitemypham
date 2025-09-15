# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beautysale', '0004_add_email_to_luckyparticipant'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image_2',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Ảnh 2'),
        ),
        migrations.AddField(
            model_name='product',
            name='image_3',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Ảnh 3'),
        ),
        migrations.AddField(
            model_name='product',
            name='image_4',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Ảnh 4'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Ảnh chính'),
        ),
    ]