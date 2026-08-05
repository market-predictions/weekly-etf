from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.etf_release_assurance import table_numeric_multiset


class ETFReleaseAssuranceScoreSurfaceTests(unittest.TestCase):
    def test_english_score_headings_match_dutch_score_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            english = root / "en.md"
            dutch = root / "nl.md"
            english.write_text(
                "\n".join(
                    [
                        "# Weekly ETF Review",
                        "### CIBR — Hold — Score 4.97 — Fresh cash: Hold — review priority 10",
                        "### GSG — Hold — Score 3.59 — Fresh cash: Hold — review priority 9",
                        "| Ticker | Value EUR | Weight % |",
                        "|---|---:|---:|",
                        "| CIBR | 20,000.00 | 19.02% |",
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
                        "| CIBR | Aanhouden | 4.97 |",
                        "| GSG | Aanhouden | 3.59 |",
                        "| Ticker | Waarde EUR | Gewicht % |",
                        "|---|---:|---:|",
                        "| CIBR | 20.000,00 | 19,02% |",
                    ]
                ),
                encoding="utf-8",
            )
            self.assertEqual(table_numeric_multiset(english), table_numeric_multiset(dutch))

    def test_score_surface_fix_does_not_hide_real_table_divergence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            english = root / "en.md"
            dutch = root / "nl.md"
            english.write_text(
                "### CIBR — Hold — Score 4.97\n"
                "| Ticker | Value EUR |\n|---|---:|\n| CIBR | 20,000.00 |\n",
                encoding="utf-8",
            )
            dutch.write_text(
                "| Ticker | Score |\n|---|---:|\n| CIBR | 4.97 |\n"
                "| Ticker | Waarde EUR |\n|---|---:|\n| CIBR | 21.000,00 |\n",
                encoding="utf-8",
            )
            self.assertNotEqual(table_numeric_multiset(english), table_numeric_multiset(dutch))


if __name__ == "__main__":
    unittest.main()
