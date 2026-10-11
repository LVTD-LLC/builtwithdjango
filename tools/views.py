import os
import subprocess
import tempfile

from django.core.management.utils import get_random_secret_key
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import TemplateView

from builtwithdjango.analytics import capture
from builtwithdjango.utils import get_builtwithdjango_logger
from newsletter.views import NewsletterSignupForm

logger = get_builtwithdjango_logger(__name__)


class GenerateDjangoSecret(TemplateView):
    template_name = "tools/generate_django_secret.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm
        return context


@csrf_protect
@require_POST
def generate_django_secret(request):
    secret_key = get_random_secret_key()
    capture(request, "django secret generated server")
    return JsonResponse({"secret_key": secret_key})


class FormatHTMLView(TemplateView):
    template_name = "tools/format_html.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm
        return context


@csrf_exempt
@require_http_methods(["POST"])
def format_html_endpoint(request):
    html_string = request.POST.get("html_string", "")

    if not html_string:
        logger.warning("[Format HTML] No HTML String provided")
        capture(request, "html formatter failed server", properties={"reason": "empty_html"})
        return JsonResponse({"error": "No HTML string provided"}, status=400)

    try:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".html", delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(html_string)

        logger.info("[Format HTML] Running djlint")

        command = ["djlint", temp_file_path, "--reformat", "--profile=django"]
        # djLint prints a source diff by default. Never send submitted code to logs.
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        # djLint returns 1 when reformatting changes a file; that is success here.
        if result.returncode not in (0, 1):
            raise subprocess.CalledProcessError(result.returncode, command)

        logger.info("[Format HTML] Finished Running djlint")
        with open(temp_file_path, "r") as file:
            logger.info("[Format HTML] Opening formatted file")
            formatted_html = file.read()

        capture(
            request,
            "html formatted server",
            properties={
                "input_length": len(html_string),
                "output_length": len(formatted_html),
            },
        )
        return JsonResponse({"formatted_html": formatted_html})

    except subprocess.TimeoutExpired:
        logger.warning("[Format HTML] Formatter timed out")
        capture(request, "html formatter failed server", properties={"reason": "timeout"})
        return JsonResponse({"error": "Formatting timed out. Try a smaller template or format it locally."}, status=504)

    except subprocess.CalledProcessError as e:
        logger.error("[Format HTML] Subprocess Error", returncode=e.returncode)
        capture(
            request,
            "html formatter failed server",
            properties={
                "reason": "djlint_error",
                "input_length": len(html_string),
            },
        )
        return JsonResponse({"error": "Could not format this template. Try formatting it locally."}, status=500)

    except Exception as e:
        logger.error("[Format HTML] Error", exception_type=e.__class__.__name__)
        capture(
            request,
            "html formatter failed server",
            properties={
                "reason": "unexpected_error",
                "input_length": len(html_string),
                "exception_type": e.__class__.__name__,
            },
        )
        return JsonResponse({"error": "Formatting is unavailable. Please try again later."}, status=500)

    finally:
        if "temp_file_path" in locals():
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.error("[Format HTML] Error deleting temporary file", exception_type=e.__class__.__name__)
