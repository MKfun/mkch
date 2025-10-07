from django.shortcuts import get_object_or_404, render
import os
import subprocess


def _get_commit_short():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=os.path.dirname(os.path.dirname(__file__))).decode().strip()
    except Exception:
        return "unknown"


COMMIT_SHORT = _get_commit_short()

def settings_view(request):
    return render(request, 'settings.html', {'nsfw': True if request.COOKIES.get('blur-nsfw') == '1' else False, 'animations': True if request.COOKIES.get('animations') == '1' else False, 'version': COMMIT_SHORT})
