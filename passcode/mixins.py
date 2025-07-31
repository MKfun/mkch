from django.contrib.admin.views.decorators import staff_member_required

class StaffRequiredMixin(object):
    @classmethod
    def as_view(self, *args, **kwargs):
        view = super(StaffRequiredMixin, self)
        return staff_member_required(view)
