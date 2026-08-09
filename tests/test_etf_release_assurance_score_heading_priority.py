from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import tools.etf_release_assurance as legacy_assurance
from tools.etf_release_assurance_score_surface import (
    install_score_heading_parity_fix,
    table_numeric_multiset,
)


class ETFReleaseAssuranceScoreHeadingPriorityTests(unittest.TestCase):
    def test_review_priority_on_english_heading_is_not_bilingual_score_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            english = root / "en.md"
            dutch = root / "nl.md"
            english.write_text(
                "\n".join(
                    [
                        "# Weekly ETF Review",
                        "### PAVE — Hold — Score 4.18 — Fresh cash: Smaller — review priority 77",
                        "### XLU — Hold — Score 3.00 — Fresh cash: No — review priority 90",
                        "| Ticker | Value EUR | Weight % |",
                        "|---|---:|---:|",
                        "| PAVE | 20,000.00 | 19.02% |",
                    ]
                ),
                encoding="utf-8",
            )
            dutch.write_text(
                "\n".join(
                    [
                        "# Wekelijkse ETF-review",
                        "| Ticker | Actie | Score |",
                        "|---|---|---:|",
                        "| PAVE | Aanhouden | 4.18 |",
                        "| XLU | Aanhouden | 3.00 |",
                        "| Ticker | Waarde EUR | Gewicht % |",
                        "|---|---:|---:|",
                        "| PAVE | 20.000,00 | 19,02% |",
                    ]
                ),
                encoding="utf-8",
            )
            self.assertEqual(table_numeric_multiset(english), table_numeric_multiset(dutch))

    def test_real_table_divergence_remains_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            english = root / "en.md"
            dutch = root / "nl.md"
            english.write_text(
                "### PAVE — Hold — Score 4.18 — review priority 77\n"
                "| Ticker | Value EUR |\n|---|---:|\n| PAVE | 20,000.00 |\n",
                encoding="utf-8",
            )
            dutch.write_text(
                "| Ticker | Score |\n|---|---:|\n| PAVE | 4.18 |\n"
                "| Ticker | Waarde EUR |\n|---|---:|\n| PAVE | 21.000,00 |\n",
                encoding="utf-8",
            )
            self.assertNotEqual(table_numeric_multiset(english), table_numeric_multiset(dutch))

    def test_installer_patches_existing_assurance_process(self) -> None:
        install_score_heading_parity_fix()
        self.assertIs(legacy_assurance.table_numeric_multiset, table_numeric_multiset)


if __name__ == "__main__":
    unittest.main()
