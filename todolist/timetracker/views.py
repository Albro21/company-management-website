from django.shortcuts import render


def timetracker(request):
    return render(request, 'timetracker/timetracker.html')