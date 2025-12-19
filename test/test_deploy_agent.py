"""Unit tests for `latoagentcore.deploy_agent`."""

from unittest.mock import MagicMock

import latoagentcore.deploy.deploy_agent as deploy_module


def test_deploy_agent_uses_session_region(monkeypatch):
    mock_session = MagicMock()
    mock_session.region_name = "us-east-1"
    monkeypatch.setattr(deploy_module, "Session", lambda: mock_session)

    mock_runtime = MagicMock()
    mock_runtime.configure.return_value = {"status": "ok"}
    monkeypatch.setattr(deploy_module, "Runtime", lambda: mock_runtime)

    resp = deploy_module.deploy_agent("my-agent", entrypoint="ep.py", requirements_file="req.txt", region=None)

    assert resp == {"status": "ok"}
    mock_runtime.configure.assert_called_once_with(
        entrypoint="ep.py",
        auto_create_execution_role=True,
        auto_create_ecr=True,
        requirements_file="req.txt",
        region="us-east-1",
        agent_name="my-agent",
    )


def test_deploy_agent_respects_explicit_region(monkeypatch):
    mock_session = MagicMock()
    mock_session.region_name = None
    monkeypatch.setattr(deploy_module, "Session", lambda: mock_session)

    mock_runtime = MagicMock()
    mock_runtime.configure.return_value = {"status": "ok"}
    monkeypatch.setattr(deploy_module, "Runtime", lambda: mock_runtime)

    resp = deploy_module.deploy_agent(
        "my-agent", entrypoint="ep.py", requirements_file="req.txt", region="eu-west-1"
    )

    assert resp == {"status": "ok"}
    mock_runtime.configure.assert_called_once_with(
        entrypoint="ep.py",
        auto_create_execution_role=True,
        auto_create_ecr=True,
        requirements_file="req.txt",
        region="eu-west-1",
        agent_name="my-agent",
    )
