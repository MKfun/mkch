from django.db import models

# tut na angl ne potomu chto spizdil a potomu chto pishu s raspberry pi

class Key(models.Model):
    class Meta:
        permissions = [
            ("generate_key", "Can generate API key")
        ]

    key = models.TextField(help_text="Api key")
