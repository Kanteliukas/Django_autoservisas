from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from . models import Profile
from . forms import UserUpdateForm, ProfileUpdateForm
from django.utils.translation import gettext_lazy as _



@login_required
def profile(request):
    return render(request, 'user_profile/profile.html')

@login_required
def update_profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, _("user profile was updated successfully"))
            return redirect(reverse_lazy('my-profile'))
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'user_profile/profile_update.html', {'u_form': u_form, 'p_form': p_form})

