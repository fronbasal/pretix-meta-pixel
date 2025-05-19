from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from pretix.base.forms import SettingsForm
from pretix.base.models import Event
from pretix.control.views.event import EventSettingsFormView, EventSettingsViewMixin


class MetaPixelSettingsForm(SettingsForm):
    meta_pixel_id = forms.CharField(
        label=_("Meta Pixel ID"),
        required=True,
        help_text=_("Your Meta Pixel ID"),
        min_length=14,
        max_length=16,
    )


class SettingsView(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    form_class = MetaPixelSettingsForm
    template_name = "pretix_meta_pixel/settings.html"
    permission = "can_change_event_settings"

    def get_success_url(self):
        return reverse(
            "plugins:pretix_meta_pixel:settings",
            kwargs={
                "organizer": self.request.event.organizer.slug,
                "event": self.request.event.slug,
            },
        )
