"""CONN-BLENDER-CONNECTOR-R005: the overlay switches the upstream to a remote endpoint.

An operator overlay named by ``SCION_UPSTREAMS_FILE`` switches the
declared stdio upstream to ``kind: http`` with a credential reference
and a TLS profile name; a literal credential refuses the overlay. The
repository ships the example as ``docs/upstreams.example.toml`` with an
unresolvable placeholder domain.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from scion_sdk.mcp.upstreams.model import UPSTREAM_DECL_INVALID, UpstreamDeclError
from scion_sdk.mcp.upstreams.overlay import merge_overlay

from blender_connector.upstreams import UPSTREAMS

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-R005")

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_example_overlay_switches_to_http() -> None:
    path = REPO_ROOT / "docs" / "upstreams.example.toml"
    assert path.is_file(), "the example overlay must be shipped in docs/"
    merged = merge_overlay(UPSTREAMS, overlay_file=path, disabled=())
    decl = merged[0]
    assert decl.kind == "http"
    assert decl.url == "https://blender.example.invalid/mcp"
    assert decl.credential == "env://BLENDER_CONNECTOR_TOKEN"
    assert decl.tls_profile == "default"
    # The namespace is inherited from the declaration.
    assert decl.effective_namespace == "blender"


def test_literal_credential_refuses_the_overlay(overlay_writer) -> None:
    text = (REPO_ROOT / "docs" / "upstreams.example.toml").read_text(encoding="utf-8")
    path = overlay_writer(
        text.replace("env://BLENDER_CONNECTOR_TOKEN", "literal-token")
    )
    with pytest.raises(UpstreamDeclError) as excinfo:
        merge_overlay(UPSTREAMS, overlay_file=path, disabled=())
    assert excinfo.value.code == UPSTREAM_DECL_INVALID
