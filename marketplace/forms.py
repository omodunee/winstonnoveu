from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Product, User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data.get("phone_number", "")
        user.address = self.cleaned_data.get("address", "")
        user.role = "customer"
        if commit:
            user.save()
        return user


class CheckoutForm(forms.Form):
    delivery_option = forms.ChoiceField(
        choices=[("pickup", "Pickup"), ("delivery", "Delivery")],
        initial="delivery",
    )
    delivery_fee = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0, initial=0)
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
    note = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)


class ProductForm(forms.ModelForm):
    image = forms.ImageField(required=True)

    class Meta:
        model = Product
        fields = [
            "category",
            "title",
            "description",
            "product_type",
            "size",
            "color",
            "material",
            "price",
            "stock",
            "image",
            "is_featured",
            "is_available",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            raise forms.ValidationError("Please upload a product image before publishing this item.")
        return image
