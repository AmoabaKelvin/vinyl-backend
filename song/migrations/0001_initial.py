# Generated by Django 4.0.5 on 2022-06-12 04:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('genre', models.CharField(max_length=100)),
                ('producer', models.CharField(max_length=150)),
                ('featured_artists', models.CharField(blank=True, max_length=255)),
                ('writer', models.CharField(blank=True, max_length=150)),
                ('release_date', models.DateField()),
                ('cover_art', models.ImageField(blank=True, upload_to='cover_arts/')),
                ('audio_file', models.FileField(upload_to='audio_files/')),
                ('track_duration', models.DurationField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='songs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
