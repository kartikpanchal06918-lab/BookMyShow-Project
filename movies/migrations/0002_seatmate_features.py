import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("movies", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="show",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bookings", to="movies.showschedule"),
        ),
        migrations.AlterField(
            model_name="review",
            name="rating",
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.CreateModel(
            name="ReviewReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reason", models.CharField(max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("reported_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="auth.user")),
                ("review", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reports", to="movies.review")),
            ],
            options={"ordering": ["-created_at"], "unique_together": {("review", "reported_by")}},
        ),
    ]
