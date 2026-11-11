from django.contrib import admin
from .models import Genre, Language, CastMember, Theater, Movie, PosterImage, ShowSchedule, Booking, Review, ReviewReport


class PosterImageInline(admin.TabularInline):
    model = PosterImage
    extra = 1


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "age_certification", "duration", "release_date")
    list_filter = ("age_certification", "release_date", "genres", "languages")
    search_fields = ("title", "description")
    filter_horizontal = ("genres", "languages", "cast_members")
    inlines = [PosterImageInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(CastMember)
class CastMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "role")
    search_fields = ("name", "role")


@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "location")
    search_fields = ("name", "city", "location")


@admin.register(ShowSchedule)
class ShowScheduleAdmin(admin.ModelAdmin):
    list_display = ("movie", "theater", "show_date", "show_time", "available_seats")
    list_filter = ("show_date", "theater")
    search_fields = ("movie__title", "theater__name", "theater__city")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "show", "status", "booked_at")
    list_filter = ("status", "booked_at")
    search_fields = ("user__username", "show__movie__title")
    list_editable = ("status",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("movie", "user", "rating", "reported", "created_at")
    list_filter = ("rating", "reported", "created_at")
    search_fields = ("movie__title", "user__username", "review_text")
    actions = ["clear_reports"]

    @admin.action(description="Clear selected review reports and make reviews visible")
    def clear_reports(self, request, queryset):
        queryset.update(reported=False, report_reason="")


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ("review", "reported_by", "reason", "created_at")
    search_fields = ("review__movie__title", "reported_by__username", "reason")
    list_filter = ("created_at",)
