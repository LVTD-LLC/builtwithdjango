from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_safe


@require_safe
def indexnow_key(request):
    # Public proof of site ownership, generated once for this site.
    response = HttpResponse(settings.INDEXNOW_KEY, content_type="text/plain; charset=utf-8")
    response["Cache-Control"] = "no-store"
    response["X-Robots-Tag"] = "noindex"
    response["X-Deployment-Revision"] = settings.DEPLOYMENT_REVISION
    return response
