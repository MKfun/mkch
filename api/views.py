import time
import json

from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Permission
from django.shortcuts import render
from django.http import JsonResponse

from .models import Key

@permission_required("key.generate_keys")
def genkey(request):
    key = Key(key=str(int(time.time()))+":"+"sex")
    key.save()

    return render(request, 'keygen.html', context={'key': key})

@csrf_exempt
def createuser(request):
    try:
        body = json.loads(request.body)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)})

    username = body['username']
    password = body['password']
    key = body['key']

    if not username or not password or not key:
        return JsonResponse({"ok": False, "error": "Please provide username, password and key in POST body."})

    if not Key.objects.filter(key=key):
        return JsonResponse({"ok": False, "error": "API Key provided in body is invalid."})

    if User.objects.filter(username=username):
        return JsonResponse({"ok": False, "error": "Username is already taken."})

    user = User.objects.create_user(username, None, password)

    cret = Permission.objects.get(name="Can create new threads")
    comt = Permission.objects.get(name="Can comment threads")
    user.user_permissions.add(cret)
    user.user_permissions.add(comt)

    user.save()
    return JsonResponse({"ok": True})
