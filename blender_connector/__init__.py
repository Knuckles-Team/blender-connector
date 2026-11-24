#!/usr/bin/env python

"""The declared Blender connector (fleet name ``blender-connector``).

One declared upstream: the popular third-party ``mcp-for-blender``
server, served behind this connector under the namespace ``blender``.
The package's skills, prompts and ontology are found by convention
under the package and served by the SDK.
"""

from scion_sdk.connector import Connector
from scion_sdk.connector_hooks import Readiness

from .upstreams import BLENDER_COMMAND, UPSTREAMS


async def _upstream_readiness() -> Readiness:
    """Report the upstream command's availability; never unseats the server.

    A missing binary reads ``not_found`` instead of failing the probe,
    and no request is made: the registry and the content stay up either
    way.
    """
    import shutil

    return Readiness(
        ready=True,
        detail={
            "upstream_command": "found" if shutil.which(BLENDER_COMMAND) else "not_found"
        },
    )


connector = Connector(
    instructions=(
        "Blender connector. Proxies the mcp-for-blender upstream; its tools "
        "are namespaced blender_* in the `blender` namespace, and the "
        "packaged Blender skill, prompts and ontology are served alongside. "
        "Call handshake for a local readiness check and registry_status for "
        "the upstream's registry state."
    ),
    tools="blender_connector.mcp",
    upstreams=UPSTREAMS,
    readiness=_upstream_readiness,
)

__all__: list[str] = ["connector"]
