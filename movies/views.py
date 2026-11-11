import re
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import F, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Movie, Booking, ShowSchedule, Review, ReviewReport
from .forms import ReviewForm, ReviewReportForm


def landing(request):
    return render(request, "movies/landing.html")


def get_youtube_embed_url(url):
    if not url:
        return None
    pattern = r"(?:youtube\.com/(?:watch\?v=|embed/)|youtu\.be/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return f"https://www.youtube-nocookie.com/embed/{match.group(1)}" if match else None


def home(request):
    movies = Movie.objects.all().order_by("-release_date")
    search = request.GET.get("q", "").strip()
    selected_genre = request.GET.get("genre", "")
    selected_language = request.GET.get("language", "")
    if search:
        movies = movies.filter(title__icontains=search)
    if selected_genre.isdigit():
        movies = movies.filter(genres__id=int(selected_genre))
    if selected_language.isdigit():
        movies = movies.filter(languages__id=int(selected_language))
    movies = movies.distinct()
    trending_movies = Movie.objects.annotate(booking_total=Count("shows__bookings")).order_by("-booking_total", "-release_date")[:6]
    recent_movies = Movie.objects.order_by("-release_date")[:6]
    from .models import Genre, Language
    context = {
        "movies": movies,
        "trending_movies": trending_movies,
        "recently_released": recent_movies,
        "genres": Genre.objects.order_by("name"),
        "languages": Language.objects.order_by("name"),
        "search": search,
        "selected_genre": selected_genre,
        "selected_language": selected_language,
    }
    return render(request, "movies/home.html", context)


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    similar_movies = Movie.objects.filter(genres__in=movie.genres.all(), languages__in=movie.languages.all()).exclude(id=movie.id).distinct()[:6]
    shows = movie.shows.filter(show_date__gte=timezone.localdate()).select_related("theater").order_by("show_date", "show_time")
    reviews = movie.reviews.filter(reported=False).select_related("user").order_by("-created_at")
    watched_user_ids = list(Booking.objects.filter(show__movie=movie, status="WATCHED").values_list("user_id", flat=True).distinct())
    user_review = None
    can_review = False
    if request.user.is_authenticated:
        can_review = Booking.objects.filter(user=request.user, show__movie=movie, status="WATCHED").exists()
        user_review = Review.objects.filter(movie=movie, user=request.user).first()
    context = {
        "movie": movie,
        "similar_movies": similar_movies,
        "trailer_embed_url": get_youtube_embed_url(movie.trailer_url),
        "shows": shows,
        "reviews": reviews,
        "watched_user_ids": watched_user_ids,
        "can_review": can_review,
        "user_review": user_review,
        "review_form": ReviewForm(instance=user_review),
        "report_form": ReviewReportForm(),
    }
    return render(request, "movies/movie_detail.html", context)


@login_required
@require_POST
def book_show(request, show_id):
    with transaction.atomic():
        show = ShowSchedule.objects.select_for_update().filter(id=show_id).first()
        if show is None:
            messages.error(request, "Show not found.")
            return redirect("home")
        show_datetime = timezone.make_aware(datetime.combine(show.show_date, show.show_time), timezone.get_current_timezone())
        if show_datetime <= timezone.now():
            messages.error(request, "You cannot book a past show.")
            return redirect("movie_detail", movie_id=show.movie.id)
        updated = ShowSchedule.objects.filter(id=show.id, available_seats__gt=0).update(available_seats=F("available_seats") - 1)
        if not updated:
            messages.error(request, "Sorry, no seats are available.")
            return redirect("movie_detail", movie_id=show.movie.id)
        Booking.objects.create(user=request.user, show=show, status="BOOKED")
    messages.success(request, "Your movie ticket has been booked successfully!")
    return redirect("my_bookings")


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related("show", "show__movie", "show__theater").order_by("-booked_at")
    return render(request, "movies/my_bookings.html", {"bookings": bookings})


@login_required
@require_POST
def save_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    eligible = Booking.objects.filter(user=request.user, show__movie=movie, status="WATCHED").exists()
    if not eligible:
        messages.error(request, "You can review this movie after your booking is marked as watched.")
        return redirect("movie_detail", movie_id=movie.id)
    review = Review.objects.filter(movie=movie, user=request.user).first()
    form = ReviewForm(request.POST, instance=review)
    if form.is_valid():
        saved = form.save(commit=False)
        saved.movie = movie
        saved.user = request.user
        saved.reported = False
        saved.report_reason = ""
        saved.save()
        messages.success(request, "Your review has been saved.")
    else:
        messages.error(request, "Please provide a valid rating and review.")
    return redirect("movie_detail", movie_id=movie.id)


@login_required
@require_POST
def report_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user_id == request.user.id:
        messages.error(request, "You cannot report your own review.")
        return redirect("movie_detail", movie_id=review.movie_id)
    form = ReviewReportForm(request.POST)
    if form.is_valid():
        report, created = ReviewReport.objects.get_or_create(review=review, reported_by=request.user, defaults={"reason": form.cleaned_data["reason"]})
        if created:
            review.reported = True
            review.report_reason = form.cleaned_data["reason"]
            review.save(update_fields=["reported", "report_reason"])
            messages.success(request, "Thank you. The review has been reported.")
        else:
            messages.info(request, "You have already reported this review.")
    else:
        messages.error(request, "Please provide a reason for reporting.")
    return redirect("movie_detail", movie_id=review.movie_id)


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your BOOKMYSHOW account has been created successfully!")
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "movies/register.html", {"form": form})
