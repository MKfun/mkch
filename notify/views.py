import json

from django.shortcuts import render
from push_notifications.models import WebPushDevice
from boards.models_tools import get_or_create_anon
from django.http.response import JsonResponse

def home(request):
    return render(request, 'not_home.html')

def register_webpush(request):
    data = json.loads(request.body)

    anon = get_or_create_anon(request)

    if not WebPushDevice.objects.filter(user=anon).exists():
        WebPushDevice.objects.create(user=anon, **data)

    return JsonResponse(status=200, data={})

def pilik_pilik(request):
    for dev in WebPushDevice.objects.all():
        print(dev.send_message)
        dev.send_message(json.dumps({"title": "Послание", "message": "Мкач клан белок"}))
    return JsonResponse(status=200, data={})
