from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_meta_pixel"
    verbose_name = "Pretix Meta Pixel"

    class PretixPluginMeta:
        name = gettext_lazy("Pretix Meta Pixel")
        author = "Daniel Malik"
        description = gettext_lazy("A crude Pretix plugin for integrating Meta Pixel tracking")
        visible = True
        version = __version__
        category = "INTEGRATION"
        compatibility = "pretix>=2.7.0"
        settings_links = []
        navigation_links = []

    def ready(self):
        from . import signals  # NOQA
