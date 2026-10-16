from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    def __str__(self):
        return str(self.id) + ' - ' + self.name

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name

class Rating(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete = models.CASCADE,
        related_name = 'ratings',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'ratings',
    )
    score = models.PositiveSmallIntegerField(
        choices = [(value, str(value)) for value in range(1,6)],
        validators = [MinValueValidator(1), MaxValueValidator(5)],
    )
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user','movie'],
                name = 'unique_user_movie_rating',
            ),
            models.CheckConstraint(
                condition = models.Q(score__gte = 1) & models.Q(score__lte = 5),
                name = 'rating_score_between_1_and_5',
            ),
        ]

    def __str__(self):
        return f'{self.user_id} - {self.movie_id}: {self.score}/5'