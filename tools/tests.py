import os
import subprocess
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase


class HTMLFormatterTests(SimpleTestCase):
    def test_formats_without_exposing_template_to_process_output_or_analytics(self):
        submitted = "<p>{{ private_value }}</p>"
        formatted = "<p>\n    {{ private_value }}\n</p>"
        paths = []

        def reformat(command, **kwargs):
            self.assertEqual(command[0], "djlint")
            self.assertEqual(command[2:], ["--reformat", "--profile=django"])
            self.assertEqual(kwargs, {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "timeout": 10})
            paths.append(command[1])
            self.assertEqual(Path(command[1]).read_text(), submitted)
            Path(command[1]).write_text(formatted)
            return subprocess.CompletedProcess(command, 1)

        with patch("tools.views.subprocess.run", side_effect=reformat), patch("tools.views.capture") as capture:
            response = self.client.post("/tools/api/format-html/", {"html_string": submitted})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"formatted_html": formatted})
        self.assertEqual(
            capture.call_args.kwargs["properties"], {"input_length": len(submitted), "output_length": len(formatted)}
        )
        self.assertFalse(os.path.exists(paths[0]))

    def test_unchanged_template_is_success(self):
        with patch("tools.views.subprocess.run", return_value=subprocess.CompletedProcess([], 0)):
            response = self.client.post("/tools/api/format-html/", {"html_string": "<p>Hello</p>"})
        self.assertEqual(response.status_code, 200)

    def test_formatter_failure_does_not_return_input_as_success(self):
        paths = []

        def fail(command, **kwargs):
            paths.append(command[1])
            return subprocess.CompletedProcess(command, 2)

        with patch("tools.views.subprocess.run", side_effect=fail):
            response = self.client.post("/tools/api/format-html/", {"html_string": "private-code"})
        self.assertEqual(response.status_code, 500)
        self.assertNotIn("private-code", response.content.decode())
        self.assertNotIn("formatted_html", response.json())
        self.assertFalse(os.path.exists(paths[0]))

    def test_timeout_is_neutral_and_removes_temporary_file(self):
        paths = []

        def timeout(command, **kwargs):
            paths.append(command[1])
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])

        with patch("tools.views.subprocess.run", side_effect=timeout):
            response = self.client.post("/tools/api/format-html/", {"html_string": "private-code"})
        self.assertEqual(response.status_code, 504)
        self.assertNotIn("private-code", response.content.decode())
        self.assertFalse(os.path.exists(paths[0]))

    def test_empty_input_does_not_start_formatter(self):
        with patch("tools.views.subprocess.run") as run:
            response = self.client.post("/tools/api/format-html/", {"html_string": ""})
        self.assertEqual(response.status_code, 400)
        run.assert_not_called()

    def test_real_djlint_formats_django_tags(self):
        source = "<ul>{% for project in projects %}<li>{{ project.name }}</li>{% empty %}<li>No projects yet.</li>{% endfor %}</ul>"
        response = self.client.post("/tools/api/format-html/", {"html_string": source})
        self.assertEqual(response.status_code, 200)
        expected = """<ul>
    {% for project in projects %}
        <li>{{ project.name }}</li>
    {% empty %}
        <li>No projects yet.</li>
    {% endfor %}
</ul>"""
        self.assertEqual(response.json()["formatted_html"].strip(), expected)
