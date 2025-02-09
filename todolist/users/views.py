from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def settings(request):
    if request.method == "POST":
        user = request.user
        
        user.username = request.POST.get("username")
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")

        if "profile_picture" in request.FILES:
            profile = user.profile
            profile.profile_picture = request.FILES["profile_picture"]
            profile.save()

        user.save()
        
        messages.success(request, "Profile settings have been updated.")
        return redirect("settings")

    return render(request, "users/settings.html")


@login_required
def profile(request):
    
    context = {
        "user": request.user,
    }
    
    return render(request, 'users/profile.html', context)
