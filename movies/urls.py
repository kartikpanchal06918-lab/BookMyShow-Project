from django.urls import path
from . import views, chatbot_views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("movie/<int:movie_id>/", views.movie_detail, name="movie_detail"),
    path("book/<int:show_id>/", views.book_show, name="book_show"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("review/<int:movie_id>/", views.save_review, name="save_review"),
    path("review/report/<int:review_id>/", views.report_review, name="report_review"),
    path("chatbot/", chatbot_views.chatbot_response, name="chatbot_response"),
    path("chatbot/my-bookings/", chatbot_views.chatbot_my_bookings, name="chatbot_my_bookings"),
]
