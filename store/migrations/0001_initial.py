# Generated by Django 4.1.7 on 2023-04-01 11:10

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('image', models.ImageField(default='store/brands/default.png', upload_to='store/brands')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=20, null=True)),
                ('subject', models.CharField(max_length=264)),
                ('message', models.TextField()),
                ('created_day', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(max_length=250, unique=True)),
                ('link', models.URLField(null=True)),
                ('image', models.ImageField(default='store/sliders/default.png', upload_to='store/sliders')),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('image', models.ImageField(default='store/images/default.png', upload_to='store/images')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.category')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('price', models.FloatField(default=0.0)),
                ('price_origin', models.FloatField(null=True)),
                ('image', models.ImageField(default='store/images/default.png', upload_to='store/images')),
                ('content', models.TextField(blank=True, null=True)),
                ('public_day', models.DateTimeField(default=django.utils.timezone.now)),
                ('viewed', models.IntegerField(default=0)),
                ('subcategory', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='store.subcategory')),
            ],
        ),
    ]
