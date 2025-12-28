from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('garten', '0004_remove_sorte_art_temp_remove_sorte_kategorie_temp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sorte',
            name='info_url',
            field=models.URLField(blank=True),
        ),
    ]
