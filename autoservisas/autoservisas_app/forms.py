from .models import OrderReview, Order
from django import forms


class OrderReviewForm(forms.ModelForm):
    class Meta:
        model = OrderReview
        fields = (
            "content",
            "order",
            "reviewer",
        )
        widgets = {"order": forms.HiddenInput(), "reviewer": forms.HiddenInput()}


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "car",
            "service",
        )
