from django.db import models

class UserPreferences(models.Model):
    preferred_genre = models.CharField(max_length=100)
    favorite_artists = models.TextField()

    def __str__(self):
        return self.preferred_genre
