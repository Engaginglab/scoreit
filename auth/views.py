import datetime
import pytz
from django.shortcuts import get_object_or_404, render_to_response
from auth.models import Profile


def activate(request, activation_key):
    """
        Activate user using his acitivation key
    """

    auth_profile = get_object_or_404(Profile, activation_key=activation_key)
    user = auth_profile.user

    if auth_profile.key_expires < datetime.datetime.now(pytz.utc):
        user.delete()
        return render_to_response('activate.html', {'expired': True})

    user.is_active = True
    user.save()
    return render_to_response('activate.html', {'success': True})
