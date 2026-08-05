from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.etf_release_assurance import build_release_assurance, validate_release_assurance


class ETFReleaseAssuranceTests(unittest.TestCase):
    def _write_report_bundle(self, root: Path, name: str, value: str = "106,644.21") -> Path:
        report = root / f"{name}.md"
        table = (
            "# Weekly ETF Review 2026-07-17\n\n"
            "| Ticker | Shares | Value EUR | Weight % |\n"
            "|---|---:|---:|---:|\n"
            f"| CIBR | 253 | {value} | 19.02% |\n"
            "| Cash | 0 | 2,534.36 | 2.38% |\n"
        )
        report.write_text(table + ("Narrative evidence. " * 80), encoding="utf-8")
        report.with_name(f"{report.stem}_delivery.html").write_text(
            "<!doctype html><html><body>" + ("validated delivery " * 100) + "</body></html>",
            encoding="utf-8",
        )
        report.with_suffix(".pdf").write_bytes(b"%PDF-" + b"0" * 2048)
        report.with_name(f"{report.stem}_equity_curve.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 256)
        return report

    def _fixture(self, root: Path, *, dutch_value: str = "106.644,21") -> dict[str, Path | str]:
        run_id = "20260719_002755"
        close_date = "2026-07-17"
        token = "260717"
        pricing = root / f"price_audit_{close_date}_{run_id}.json"
        runtime = root / f"etf_report_state_{token}_{run_id}.json"
        manifest = root / f"weekly_etf_run_manifest_{close_date}_{run_id}.json"
        portfolio = root / "etf_portfolio_state.json"
        ledger = root / "etf_trade_ledger.csv"
        en = self._write_report_bundle(root, "weekly_analysis_pro_260717_04")
        nl = self._write_report_bundle(root, "weekly_analysis_pro_nl_260717_04", value=dutch_value)

        pricing.write_text(json.dumps({"requested_close_date": close_date, "run_id": run_id}), encoding="utf-8")
        runtime.write_text(
            json.dumps({"report_date": close_date, "pricing_audit_source": str(pricing)}),
            encoding="utf-8",
        )
        manifest.write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "requested_close_date": close_date,
                    "report_token": token,
                    "pricing_audit_path": str(pricing),
                    "runtime_state_path": str(runtime),
                    "english_report_path": str(en),
                    "dutch_report_path": str(nl),
                }
            ),
            encoding="utf-8",
        )
        portfolio.write_text(json.dumps({"positions": [{"ticker": "CIBR", "shares": 253}]}), encoding="utf-8")
        ledger.write_text("date,ticker,shares\n2026-07-17,CIBR,253\n", encoding="utf-8")
        return {
            "source_sha": "a" * 40,
            "run_id": run_id,
            "close_date": close_date,
            "token": token,
            "pricing": pricing,
            "runtime": runtime,
            "manifest": manifest,
            "portfolio": portfolio,
            "ledger": ledger,
            "en": en,
            "nl": nl,
        }

    def test_valid_candidate_passes_and_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fx = self._fixture(root)
            output = root / "assurance.json"
            record = build_release_assurance(
                source_sha=str(fx["source_sha"]),
                github_run_id="12345",
                run_id=str(fx["run_id"]),
                requested_close_date=str(fx["close_date"]),
                report_token=str(fx["token"]),
                pricing_audit=Path(fx["pricing"]),
                runtime_state=Path(fx["runtime"]),
                run_manifest=Path(fx["manifest"]),
                portfolio_state=Path(fx["portfolio"]),
                trade_ledger=Path(fx["ledger"]),
                english_report=Path(fx["en"]),
                dutch_report=Path(fx["nl"]),
                output=output,
            )
            self.assertEqual(record["decision"], "PASS")
            validate_release_assurance(
                output,
                expected_source_sha=str(fx["source_sha"]),
                expected_run_id=str(fx["run_id"]),
                expected_close_date=str(fx["close_date"]),
                expected_report_token=str(fx["token"]),
            )

    def test_bilingual_numeric_divergence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fx = self._fixture(root, dutch_value="99.999,99")
            output = root / "assurance.json"
            record = build_release_assurance(
                source_sha=str(fx["source_sha"]),
                github_run_id="12345",
                run_id=str(fx["run_id"]),
                requested_close_date=str(fx["close_date"]),
                report_token=str(fx["token"]),
                pricing_audit=Path(fx["pricing"]),
                runtime_state=Path(fx["runtime"]),
                run_manifest=Path(fx["manifest"]),
                portfolio_state=Path(fx["portfolio"]),
                trade_ledger=Path(fx["ledger"]),
                english_report=Path(fx["en"]),
                dutch_report=Path(fx["nl"]),
                output=output,
            )
            self.assertEqual(record["decision"], "FAIL")
            self.assertIn("bilingual_table_numeric_parity", record["blockers"])
            with self.assertRaises(RuntimeError):
                validate_release_assurance(output)

    def test_planted_fail_record_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "failed.json"
            path.write_text(
                json.dumps(
                    {
                        "decision": "FAIL",
                        "implementation_role": "implementation_operations",
                        "assurance_role": "governance_release_assurance",
                        "identity": {},
                        "checks": [],
                        "artifact_hashes": {},
                        "blockers": ["planted_failure"],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(RuntimeError):
                validate_release_assurance(path)


if __name__ == "__main__":
    unittest.main()
