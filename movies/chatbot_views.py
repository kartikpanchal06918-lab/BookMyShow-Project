import json
import re
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Movie, Booking

GENRE_ALIASES = {
    "action": ["action", "एक्शन"],
    "comedy": ["comedy", "कॉमेडी", "हasi", "हंसी"],
    "horror": ["horror", "भूत", "डरावनी", "हॉरर"],
    "romance": ["romance", "romantic", "रोमांस", "प्यार"],
    "drama": ["drama", "ड्रामा"],
    "thriller": ["thriller", "थ्रिलर"],
    "animation": ["animation", "animated", "एनीमेशन", "कार्टून"],
}


def _movie_payload(movie):
    poster = movie.posters.first()
    return {
        "title": movie.title,
        "url": f"/movie/{movie.id}/",
        "poster": poster.image.url if poster and poster.image else "",
        "rating": movie.average_rating,
    }


@require_POST
def chatbot_response(request):
    try:
        data = json.loads(request.body or "{}")
        message = str(data.get("message", "")).strip()
    except (json.JSONDecodeError, AttributeError, TypeError):
        return JsonResponse({"reply": "Please send a valid message.", "movies": []}, status=400)

    if not message:
        return JsonResponse({"reply": "Please type or speak a question.", "movies": []})

    normalized = message.lower()
    if re.search(r"\b(hello|hi|hey)\b", normalized) or any(word in normalized for word in ["नमस्ते", "हेलो"]):
        return JsonResponse({"reply": "Hello! Welcome to BookMyShow. Ask me to find a movie or help with bookings.", "movies": []})

    if any(word in normalized for word in ["my booking", "my bookings", "my ticket", "meri booking", "meri bookings", "मेरी बुकिंग", "मेरे टिकट"]):
        if not request.user.is_authenticated:
            return JsonResponse({"reply": "Please log in to view your bookings.", "movies": [], "login_url": "/accounts/login/"})
        bookings = Booking.objects.filter(user=request.user).exclude(status="CANCELLED").select_related("show__movie").order_by("-booked_at")[:5]
        titles = [item.show.movie.title for item in bookings]
        return JsonResponse({"reply": "Your recent bookings: " + ", ".join(titles) if titles else "You do not have any bookings yet.", "movies": []})

    if any(word in normalized for word in ["booking", "book ticket", "book a ticket", "ticket", "बुकिंग", "टिकट"]):
        return JsonResponse({"reply": "To book a ticket, open a movie, choose an available show and select Book 1 Seat. Sign in first. You can view your tickets under My Bookings.", "movies": []})

    for genre_name, aliases in GENRE_ALIASES.items():
        if any(alias in normalized for alias in aliases):
            movies = Movie.objects.filter(genres__name__icontains=genre_name).distinct().order_by("-release_date")[:5]
            if movies:
                return JsonResponse({"reply": f"Here are some {genre_name} movies available:", "movies": [_movie_payload(movie) for movie in movies]})
            return JsonResponse({"reply": f"I couldn't find any {genre_name} movies in the catalogue yet.", "movies": []})

    cleaned = re.sub(r"\b(show me|show|find|search for|search|movie|movies|please|mujhe|dikhao|batao)\b", " ", normalized, flags=re.I).strip()
    search_text = cleaned or message
    matches = Movie.objects.filter(title__icontains=search_text).distinct().order_by("-release_date")[:5]
    if matches:
        return JsonResponse({"reply": "I found these matching movies:", "movies": [_movie_payload(movie) for movie in matches]})

    return JsonResponse({"reply": "I can help you search movies by title or genre, explain ticket booking, and check your bookings. Try: Show comedy movies.", "movies": []})


@login_required
@require_POST
def chatbot_my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).exclude(status="CANCELLED").select_related("show__movie").order_by("-booked_at")[:10]
    titles = [item.show.movie.title for item in bookings]
    return JsonResponse({"reply": "Your bookings: " + ", ".join(titles) if titles else "You do not have any bookings yet."})
