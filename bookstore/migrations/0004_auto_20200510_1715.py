# Generated by Django 3.0.5 on 2020-05-10 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore', '0003_auto_20200510_1652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bookstore.Category', verbose_name='类别'),
        ),
    ]
