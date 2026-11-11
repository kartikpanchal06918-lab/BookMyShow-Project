import json
from datetime import date, time, timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Genre, Language, Movie, Theater, ShowSchedule, Booking, Review


class BookMyShowCoreTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="StrongPass123!")
        self.genre = Genre.objects.create(name="Comedy")
        self.language = Language.objects.create(name="Hindi")
        self.movie = Movie.objects.create(title="Test Comedy", age_certification="U", duration=120, description="Test movie", release_date=date.today())
        self.movie.genres.add(self.genre)
        self.movie.languages.add(self.language)
        self.theater = Theater.objects.create(name="Test Cinema", location="Main Road", city="Delhi")
        self.show = ShowSchedule.objects.create(movie=self.movie, theater=self.theater, show_date=date.today() + timedelta(days=2), show_time=time(18, 0), available_seats=2)

    def test_landing_page_loads(self):
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_loads_with_movie_filters(self):
        response = self.client.get(reverse("home"), {"q": "Test", "genre": str(self.genre.id)})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Comedy")

    def test_chatbot_finds_genre_movies(self):
        response = self.client.post(reverse("chatbot_response"), data=json.dumps({"message": "Show comedy movies"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["movies"][0]["title"], "Test Comedy")

    def test_chatbot_gives_booking_guidance(self):
        response = self.client.post(reverse("chatbot_response"), data=json.dumps({"message": "How do I book a ticket?"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("book", response.json()["reply"].lower())

    def test_movie_detail_page_loads(self):
        response = self.client.get(reverse("movie_detail", args=[self.movie.id]))
        self.assertEqual(response.status_code, 200)

    def test_booking_requires_login(self):
        response = self.client.post(reverse("book_show", args=[self.show.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Booking.objects.count(), 0)

    def test_logged_in_user_can_book_available_show(self):
        self.client.login(username="tester", password="StrongPass123!")
        response = self.client.post(reverse("book_show", args=[self.show.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Booking.objects.filter(user=self.user).count(), 1)
        self.show.refresh_from_db()
        self.assertEqual(self.show.available_seats, 1)

    def test_review_requires_watched_booking(self):
        self.client.login(username="tester", password="StrongPass123!")
        response = self.client.post(reverse("save_review", args=[self.movie.id]), {"rating": 5, "review_text": "Great movie"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)

    def test_review_allowed_after_watched_booking(self):
        Booking.objects.create(user=self.user, show=self.show, status="WATCHED")
        self.client.login(username="tester", password="StrongPass123!")
        response = self.client.post(reverse("save_review", args=[self.movie.id]), {"rating": 5, "review_text": "Great movie"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)
    def test_chatbot_supports_hindi_genre_keyword(self):
        response = self.client.post(reverse("chatbot_response"), data=json.dumps({"message": "मुझे कॉमेडी फिल्में दिखाओ"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["movies"][0]["title"], "Test Comedy")

    def test_chatbot_returns_signed_in_users_bookings(self):
        Booking.objects.create(user=self.user, show=self.show, status="BOOKED")
        self.client.login(username="tester", password="StrongPass123!")
        response = self.client.post(reverse("chatbot_response"), data=json.dumps({"message": "Show my bookings"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Comedy", response.json()["reply"])

    def test_chatbot_widget_is_present_on_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "BookMyShow Assistant")
        self.assertContains(response, "bms-mic")

