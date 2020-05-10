# Generated by Django 3.0.5 on 2020-05-10 08:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore', '0002_auto_20200508_2139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='类别')),
            ],
            options={
                'verbose_name': '类别',
                'verbose_name_plural': '类别',
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['name', 'publisher', 'category'], 'verbose_name': '图书信息', 'verbose_name_plural': '图书信息'},
        ),
        migrations.AlterField(
            model_name='publisher',
            name='name',
            field=models.CharField(max_length=30, verbose_name='出版社'),
        ),
        migrations.AddField(
            model_name='book',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='bookstore.Category', verbose_name='类别'),
        ),
    ]
