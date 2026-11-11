# BOOKMYSHOW – Movie Management and Booking System

BOOKMYSHOW is a Django-based movie discovery and booking project. It includes movie administration, multiple posters, YouTube trailer embedding, genres, languages, cast, theatres, show schedules, user accounts, bookings, watched-only reviews and ratings, review reports, verified-viewer badges, trending movies, similar movies, and recently released movies.

## Requirements
- Python 3.10 or newer
- Django (see `requirements.txt`)
- Pillow

## Run on Windows
1. Extract the project ZIP.
2. Open the extracted `bookmy show` folder in VS Code.
3. Open the VS Code terminal in that folder.
4. Create and activate a virtual environment:

   ```powershell
   py -m venv venv
   .\venv\Scripts\activate
   ```
5. Install packages:

   ```powershell
   pip install -r requirements.txt
   ```
6. Apply database migrations:

   ```powershell
   python manage.py migrate
   ```
7. Create an administrator:

   ```powershell
   python manage.py createsuperuser
   ```
8. Start the website:

   ```powershell
   python manage.py runserver
   ```
9. Open `http://127.0.0.1:8000/`. The admin panel is at `http://127.0.0.1:8000/admin/`.

## Add project data
In the admin panel, add Genres, Languages, Cast Members, Theatres, and Movies. Open a Movie to add its genres, languages, cast, trailer URL, description, certification, duration, release date, and one or more poster images. Then add Show Schedules with a future date, time, and available seat count.

## Booking and verified reviews
A signed-in user can book one seat from a scheduled show. In the admin panel, open Bookings and change the booking status from `Booked` to `Watched` after the movie has been watched. Only then can that user submit or edit a rating/review. A watched booking is also used to display the Verified Viewer badge. Reported reviews are hidden from the public page until an administrator clears the report.

## Notes
- The included SQLite database and media files are retained from the supplied project archive.
- The site uses Django's built-in authentication views. Registration is available at `/register/`.
- The YouTube trailer helper accepts standard YouTube watch, short, and embed URLs and converts valid video IDs to the privacy-enhanced `youtube-nocookie.com` embed host.
- Before public deployment, set `DEBUG=False`, configure `ALLOWED_HOSTS`, use a new secret key stored in an environment variable, configure HTTPS/security settings, and use a production database and static/media hosting. Do not publish the original secret key from the supplied settings file.

## Chatbot and voice assistant
A floating BookMyShow assistant is available on the home, movie details, and My Bookings pages. It can search the local movie catalogue by title and supported genres, explain the booking process, and (when signed in) report recent bookings. The microphone uses the browser Web Speech API; choose English or Hindi before speaking. Spoken replies use the browser Speech Synthesis API. Voice recognition support depends on the browser and microphone permission; use a current Chrome or Edge browser over localhost or HTTPS. This is a rule-based assistant connected to the Django database, not an external generative-AI service.

## Automated tests
Run `python manage.py check` and `python manage.py test movies`. The test suite covers page loading, catalogue filtering, chatbot genre search and booking guidance, login-required booking, seat count updates, and watched-booking review eligibility. Also manually test microphone permission, spoken replies, and the layout at mobile/tablet widths because browser voice support and visual responsiveness are not fully covered by Django tests.
