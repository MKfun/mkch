# Generated manually for PoW security updates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pow', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='powchallenge',
            name='session_key',
            field=models.CharField(default='', max_length=40, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='powchallenge',
            name='hmac_signature',
            field=models.CharField(default='', max_length=64),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='powchallenge',
            name='difficulty',
            field=models.IntegerField(default=20),
        ),
    ]
