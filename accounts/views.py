from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import SignUpForm

def signup(request):
    if request.user.is_authenticated:
        return redirect("event_list")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after successful registration
            messages.success(request, "Welcome to StagePass! Your account is ready.")
            return redirect("event_list")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})
