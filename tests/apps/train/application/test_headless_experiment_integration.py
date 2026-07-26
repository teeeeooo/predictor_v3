"""Targeted real subprocess and machine-readable Phase 5F integration."""

from __future__ import annotations

import json
import threading
import time

from apps.train.application.experiments.campaign import CampaignApplicationService
from apps.train.composition.experiments import build_headless_experiment_service
from apps.train.interfaces.headless.cli import main
from apps.common.model_lifecycle import default_model_lifecycle_root
from tools.dev.mock_smoke.generators import write_mock_training_data


def _spec(data_path, *, campaign=None):  # noqa: ANN001
    return {
        "schema_version": "predictor_v3.experiment.v1",
        "experiment": {"name": "headless-integration", "purpose": "test"},
        "data": {"source_path": str(data_path)},
        **({"campaign": campaign} if campaign else {}),
    }


def test_real_headless_subprocess_reuses_candidate_publication_and_cli_read(
    tmp_path, capsys, monkeypatch
):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    lifecycle_root = default_model_lifecycle_root()
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    service = build_headless_experiment_service(
        generation_root=tmp_path / "generations",
        lifecycle_root=lifecycle_root,
        extra_training_args=("--dev-fast", "--dev-rows", "8"),
    )

    service.run(_spec(data), run_id="real-headless-run")
    exit_status = main(["run-result", "real-headless-run"])
    output = json.loads(capsys.readouterr().out)
    artifacts_status = main(["run-artifacts", "real-headless-run"])
    artifacts = json.loads(capsys.readouterr().out)
    logs_status = main(["run-logs", "real-headless-run"])
    logs = json.loads(capsys.readouterr().out)

    assert exit_status == 0
    assert output["schema_version"] == "predictor_v3.experiment_output.v1"
    assert output["outcome"] == "success"
    assert output["message"] != output["diagnostics"]
    assert output["data"]["training_started"] is True
    assert output["data"]["result"]["candidate_reference"] == (
        "candidate-real-headless-run"
    )
    assert artifacts_status == 0
    assert any(
        item["category"] == "training_report"
        for item in artifacts["data"]["analysis_artifacts"]
    )
    assert logs_status == 0
    assert logs["data"]["log_reference"].startswith("experiments/runs/")
    assert logs["data"]["events"]
    assert (
        lifecycle_root
        / "candidates"
        / "candidate-real-headless-run"
        / "training_report.xlsx"
    ).is_file()


def test_campaign_cancel_before_real_training_start_preserves_budget_and_evidence(
    tmp_path,
):
    campaign_id = "real-cancel-campaign"
    lifecycle_root = tmp_path / "lifecycle"
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    service = build_headless_experiment_service(
        generation_root=tmp_path / "generations",
        lifecycle_root=lifecycle_root,
        campaign_id=campaign_id,
        extra_training_args=("--hang-before-start",),
    )
    campaigns = CampaignApplicationService(service)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 1,
            "experiments": [{"experiment": {"name": "cancel-me"}}],
        },
    )
    result = {}

    def execute() -> None:
        result["record"] = campaigns.start(
            specification, campaign_id=campaign_id
        )

    worker = threading.Thread(target=execute)
    worker.start()
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            if campaigns.status(campaign_id)["status"] == "running":
                break
        except FileNotFoundError:
            pass
        time.sleep(0.05)
    else:
        raise AssertionError("campaign did not start its current process")

    campaigns.cancel(campaign_id)
    worker.join(timeout=15)

    assert not worker.is_alive()
    assert result["record"]["status"] == "failed_resumable"
    assert result["record"]["failure"]["code"] == "training_start_failed"
    assert result["record"]["budget"]["consumed_iterations"] == 0
    assert result["record"]["completed_runs"] == []
    assert result["record"]["attempt_history"][0]["training_started"] is False
    assert not (lifecycle_root / "candidates").exists()
    evidence = (
        lifecycle_root
        / "run_evidence"
        / f"{campaign_id}-iteration-1-attempt-1"
        / "training_result.json"
    )
    assert evidence.is_file()
