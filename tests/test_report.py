"""Prevent partial experiment outputs from being labelled a completed report."""
import json
import pytest
import grokking.report as report


def test_final_report_requires_completed_raw_trace_audit(tmp_path,monkeypatch):
    monkeypatch.setattr(report,'ROOT',tmp_path)
    out=tmp_path/'output/review2';out.mkdir(parents=True)
    (out/'audit.json').write_text(json.dumps(dict(status='passed',mode='review2',completed_main_runs=119)))
    with pytest.raises(ValueError,match='completed raw-trace audit'):
        report.build('review2')
    assert not (tmp_path/'output/pdf/review2_report.pdf').exists()
