# BookMyShow project testing report

## Automated checks performed
- `python manage.py check` — PASS (no system-check issues).
- `python manage.py test movies` — PASS (12 tests passed).
- JavaScript syntax check with `node --check movies/static/movies/chatbot.js` — PASS.

## Test coverage
1. Landing page loads.
2. Home page loads and catalogue filters return matching movies.
3. Movie details page loads with its required context.
4. Chatbot finds movies by genre in English.
5. Chatbot finds movies using a Hindi genre keyword.
6. Chatbot returns ticket-booking guidance.
7. Chatbot can return a signed-in user's booking list.
8. Chatbot widget and microphone control are present on the home page.
9. Booking is blocked for logged-out users.
10. Signed-in user can book an available show and the available-seat count decreases.
11. Review submission is blocked until a booking is marked WATCHED.
12. Review submission succeeds after a booking is marked WATCHED.

## Manual checks still required on the user's computer
- Allow microphone access in Chrome or Edge and test English and Hindi recognition.
- Confirm spoken replies are audible and understandable.
- Check the website at phone, tablet, and desktop widths.
- Test the live deployed website after deployment, including media/poster loading and login/session behavior.
- Verify that the deployment uses HTTPS. Browser microphone recognition generally requires localhost or a secure HTTPS origin.

## Important deployment note
The supplied settings are configured for local development (`DEBUG=True`, empty `ALLOWED_HOSTS`, and a development secret key). Do not deploy with these settings. Configure a private production secret key, `DEBUG=False`, the deployed hostname in `ALLOWED_HOSTS`, HTTPS, and persistent database/media storage before publishing the site.
