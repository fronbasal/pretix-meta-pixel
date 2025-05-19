import logging
import secrets
from base64 import b64encode

from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _

# noinspection PyProtectedMember
from pretix.base.middleware import _merge_csp, _parse_csp, _render_csp
from pretix.control.signals import nav_event_settings
from pretix.presale.signals import html_page_header, process_response

logger = logging.getLogger(__name__)


@receiver(nav_event_settings, dispatch_uid="meta_pixel_nav_event_settings")
def navbar_event_settings(sender, request, **kwargs):
    url = resolve(request.path_info)
    return [
        {
            "label": _("Meta Pixel"),
            "url": reverse(
                "plugins:pretix_meta_pixel:settings",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.organizer.slug,
                },
            ),
            "active": url.namespace == "plugins:pretix_meta_pixel"
                      and url.url_name.startswith("settings"),
        }
    ]


@receiver(html_page_header, dispatch_uid="meta_pixel_html_page_header")
def html_page_header_presale(sender, request, **kwargs):
    pixel_id = sender.settings.get("meta_pixel_id")

    if not pixel_id:
        return ""

    script_content = f"""
    !function(f,b,e,v,n,t,s)
    {{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
    if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
    n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t,s)}}(window, document,'script',
    'https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', '{pixel_id}');
    fbq('track', 'PageView');
    """
    noscript_content = f"""
    <noscript><img height="1" width="1" style="display:none"
    src="https://www.facebook.com/tr?id={pixel_id}&ev=PageView&noscript=1"/></noscript>
    """

    nonce = b64encode(secrets.token_bytes(16)).decode()
    request._meta_pixel_script_nonce = nonce
    print("Nonce for Meta Pixel script:", nonce)
    return f'<script nonce="{nonce}">{script_content}</script>{noscript_content}'


@receiver(process_response, dispatch_uid="meta_pixel_process_response")
def process_response_presale_csp(sender, request, response, **kwargs):
    pixel_id = sender.settings.get("meta_pixel_id")
    if not pixel_id:
        return response

    if "Content-Security-Policy" in response:
        headers = _parse_csp(response["Content-Security-Policy"])
    else:
        headers = {}

    script_nonce = getattr(request, "_meta_pixel_script_nonce", None)
    if script_nonce:
        _merge_csp(headers, {"script-src": [f"'nonce-{script_nonce}'"]})

    print("Found nonce for Meta Pixel script: ", script_nonce)

    _merge_csp(
        headers,
        {
            "script-src": [
                "https://connect.facebook.net",
                # Bad quick fix.
                "'unsafe-eval'",
            ],
            "img-src": [
                "https://www.facebook.com",
            ],
        },
    )

    if headers:
        response["Content-Security-Policy"] = _render_csp(headers)

    return response
