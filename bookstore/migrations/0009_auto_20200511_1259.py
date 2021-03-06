# Generated by Django 3.0.5 on 2020-05-11 04:59

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bookstore', '0008_auto_20200510_2226'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin',
            name='phone',
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(help_text='请输入中国大陆11位手机号', max_length=11, validators=[django.core.validators.RegexValidator(message='请确保手机号格式正确！', regex='^1(3|5|7|8|9)\\d{9}$')], verbose_name='联系方式（手机）')),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='管理员姓名')),
            ],
            options={
                'verbose_name': '联系方式',
                'verbose_name_plural': '联系方式',
            },
        ),
    ]
