# Generated by Django 2.2.4 on 2019-12-31 03:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminpage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='tahun_ajaran_aktif',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('tahun_aktif', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='adminpage.tahun_ajaran')),
            ],
        ),
    ]