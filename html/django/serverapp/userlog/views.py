from django.shortcuts import render
from django.http import HttpResponse

from .models import ActionLog

def index(request):
    output = "<h1>Logged messages (by user):</h1>"
    lis = ActionLog.objects.order_by('-created')[:10]
    output += "</p>".join([f"{q.created} <b>{q.user}</b>: {q.msg}" for q in lis])
    output += "</p>"
    return HttpResponse(output)


def log(request, user, msg):
    ActionLog.objects.create(user=user, msg=msg)
    msg = f"You're logging user=[{user}], msg=[{msg}]"
    return HttpResponse(msg)