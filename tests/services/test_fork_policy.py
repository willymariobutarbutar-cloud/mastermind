"""Mastermind fork: upstream release checks stay informational, never self-install."""

from __future__ import annotations

import pytest

from deeptutor.api.routers import system as system_router
from deeptutor.services import app_update
from deeptutor.services.app_update import Installation
from deeptutor.services.fork_policy import (
    FORK_REPO_URL,
    FORK_UPGRADE_COMMAND,
    apply_fork_policy,
)


def _installation(mode: str, *, automatic: bool) -> Installation:
    return Installation(
        mode=mode,  # type: ignore[arg-type]
        current_version="1.7.2",
        automatic_update=automatic,
        command="pip install -U deeptutor",
        reason="",
    )


@pytest.mark.parametrize("mode", ["pypi", "source", "docker", "unknown"])
def test_fork_policy_disables_automatic_update_for_every_mode(mode: str) -> None:
    result = apply_fork_policy(_installation(mode, automatic=True))

    assert result.automatic_update is False
    assert result.mode == mode
    assert result.current_version == "1.7.2"


def test_fork_policy_replaces_pypi_command_with_upstream_merge() -> None:
    result = apply_fork_policy(_installation("pypi", automatic=True))

    assert result.command == FORK_UPGRADE_COMMAND
    assert "pip install -U deeptutor" not in result.command
    assert "git fetch upstream" in result.command
    assert "rebrand.py" in result.command
    assert "Mastermind" in result.reason
    assert "upstream" in result.reason.lower()


def test_fork_policy_returns_new_object_without_mutating_input() -> None:
    original = _installation("pypi", automatic=True)

    result = apply_fork_policy(original)

    assert result is not original
    assert original.automatic_update is True
    assert original.command == "pip install -U deeptutor"


def test_fork_repo_url_points_at_the_fork_not_upstream() -> None:
    assert FORK_REPO_URL.startswith("https://github.com/")
    assert "HKUDS" not in FORK_REPO_URL


def test_router_installation_is_always_fork_managed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        system_router, "detect_installation", lambda: _installation("pypi", automatic=True)
    )

    installation = system_router.get_update_installation()

    assert installation.automatic_update is False
    assert installation.command == FORK_UPGRADE_COMMAND


def test_upstream_release_source_is_unchanged() -> None:
    # Checks still read upstream releases: that is the signal to merge a new tag.
    assert "HKUDS/DeepTutor" in app_update.GITHUB_LATEST_RELEASE_URL
