# Generated by Django 3.0 on 2019-12-10 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_vintage_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Winery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=250, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('sort', models.IntegerField(blank=True, default=0, null=True, verbose_name='Sort')),
            ],
            options={
                'verbose_name': 'Winery',
                'verbose_name_plural': 'Winery-plural',
                'ordering': ('sort',),
            },
        ),
    ]