import os
import subprocess
import sys
from pathlib import Path


def test_openapi_schema_generation_has_no_warnings(tmp_path):
    """Contract test: schema generation should be warning-free (fail-on-warn)."""

    backend_dir = Path(__file__).resolve().parents[3]
    schema_path = tmp_path / "openapi.generated.yaml"

    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "project.settings.test"

    result = subprocess.run(
        [
            sys.executable,
            "manage.py",
            "spectacular",
            "--file",
            str(schema_path),
            "--validate",
            "--fail-on-warn",
        ],
        cwd=str(backend_dir),
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        "OpenAPI schema generation must succeed without warnings.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}\n"
    )
