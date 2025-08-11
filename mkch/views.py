from django.shortcuts import get_object_or_404, render

def settings_view(request):
    return render(request, 'settings.html', {'nsfw': True if request.COOKIES.get("blur-nsfw") == "1" else False})
