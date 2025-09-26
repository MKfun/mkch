from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.conf import settings

class StaffMemberRequiredMixin(object):
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_active and request.user.is_staff):
            messages.error(request, 'Сюда можно только админам.')
            return redirect(settings.LOGIN_URL)
        return super(StaffMemberRequiredMixin, self).dispatch(request, *args, **kwargs)
