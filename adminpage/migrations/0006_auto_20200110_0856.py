# Generated by Django 2.2.4 on 2020-01-10 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpage', '0005_auto_20200107_0020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tabel_siswa',
            name='foto',
            field=models.ImageField(upload_to=''),
        ),
    ]
