"""Mastermind fork policy for the in-app update flow.

Mastermind is a rebranded fork of HKUDS/DeepTutor and is never published to
PyPI. The upstream updater would run ``pip install -U deeptutor``, which
replaces this fork with upstream DeepTutor and silently drops the rebrand.
This module keeps upstream release checks as an informational signal ("a new
upstream tag exists, merge it") and removes every self-install path.

Kept in its own file so upstream merges only touch a one-line hook in
``deeptutor/api/routers/system.py``.
"""

from __future__ import annotations

from dataclasses import replace

from deeptutor.services.app_update import Installation

FORK_NAME = "Mastermind"
FORK_REPO_URL = "https://github.com/willymariobutarbutar-cloud/mastermind"
FORK_UPGRADE_COMMAND = (
    "git fetch upstream --tags && git merge <upstream-tag> "
    "&& python3 -I scripts/mastermind/rebrand.py . && pip install -e . --no-deps "
    "&& mastermind stop && mastermind start --detach"
)
FORK_UPDATE_REASON = (
    "Mastermind is a fork of DeepTutor. The release shown here is the latest "
    "upstream DeepTutor release. Merge it into the mastermind branch and rerun "
    "the rebrand script; in-app updates are disabled so they cannot overwrite "
    "the fork with upstream DeepTutor."
)


def apply_fork_policy(installation: Installation) -> Installation:
    """Return a copy of ``installation`` that can never self-update."""
    return replace(
        installation,
        automatic_update=False,
        command=FORK_UPGRADE_COMMAND,
        reason=FORK_UPDATE_REASON,
    )


__all__ = [
    "FORK_NAME",
    "FORK_REPO_URL",
    "FORK_UPDATE_REASON",
    "FORK_UPGRADE_COMMAND",
    "apply_fork_policy",
]
