from django import forms
from .models import Review, ReviewReport


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "review_text"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} / 5") for i in range(1, 6)]),
            "review_text": forms.Textarea(attrs={"rows": 4, "placeholder": "Share your experience..."}),
        }


class ReviewReportForm(forms.ModelForm):
    class Meta:
        model = ReviewReport
        fields = ["reason"]
        widgets = {"reason": forms.Textarea(attrs={"rows": 3, "placeholder": "Why are you reporting this review?"})}
