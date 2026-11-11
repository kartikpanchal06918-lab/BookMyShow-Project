from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class CastMember(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to="cast/", blank=True, null=True)

    def __str__(self):
        return self.name


class Theater(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=250)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.city}"


class Movie(models.Model):
    AGE_CHOICES = [("U", "U"), ("UA", "UA"), ("A", "A")]
    title = models.CharField(max_length=200)
    genres = models.ManyToManyField(Genre)
    languages = models.ManyToManyField(Language)
    cast_members = models.ManyToManyField(CastMember, blank=True)
    trailer_url = models.URLField(blank=True)
    age_certification = models.CharField(max_length=10, choices=AGE_CHOICES)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    description = models.TextField()
    release_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def average_rating(self):
        result = self.reviews.filter(reported=False).aggregate(value=Avg("rating"))
        return round(result["value"], 1) if result["value"] is not None else None

    @property
    def review_count(self):
        return self.reviews.filter(reported=False).count()

    def __str__(self):
        return self.title


class PosterImage(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="posters")
    image = models.ImageField(upload_to="posters/")
    alt_text = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.movie.title} Poster"


class ShowSchedule(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="shows")
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name="shows")
    show_date = models.DateField()
    show_time = models.TimeField()
    available_seats = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.movie.title} - {self.theater.name}"


class Booking(models.Model):
    STATUS_CHOICES = [("BOOKED", "Booked"), ("WATCHED", "Watched"), ("CANCELLED", "Cancelled")]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    show = models.ForeignKey(ShowSchedule, on_delete=models.CASCADE, related_name="bookings")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="BOOKED")
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.show.movie.title}"


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()
    reported = models.BooleanField(default=False)
    report_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("movie", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.movie.title} - {self.user.username} - {self.rating}/5"


class ReviewReport(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="reports")
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("review", "reported_by")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report on review #{self.review_id}"
