import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import test_etf_release_assurance as assurance_tests
from tools.etf_release_assurance import build_release_assurance
from tools.wro_operator_status import operator_status


class OperatorStatusTests(unittest.TestCase):
    def test_cli_text_preserves_package_blockers_exit_code_and_no_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            assurance = Path(tmp) / 'assurance.json'
            fx = assurance_tests.ETFReleaseAssuranceTests()._fixture(Path(tmp))
            build_release_assurance(
                source_sha=fx['source_sha'], github_run_id='123', run_id=fx['run_id'],
                requested_close_date=fx['close_date'], report_token=fx['token'],
                pricing_audit=fx['pricing'], runtime_state=fx['runtime'], run_manifest=fx['manifest'],
                portfolio_state=fx['portfolio'], trade_ledger=fx['ledger'],
                english_report=fx['en'], dutch_report=fx['nl'], output=assurance)
            command = [
                sys.executable, '-m', 'tools.wro_operator_status',
                '--assurance', str(assurance), '--source-sha', 'a' * 40,
                '--run-id', fx['run_id'], '--close-date', '2026-07-17',
                '--report-token', '260717',
            ]
            before = {p: p.read_bytes() for p in Path(tmp).iterdir()}
            default = subprocess.run(command, capture_output=True, text=True)
            explicit = subprocess.run(command + ['--format', 'json'],
                                      capture_output=True, text=True)
            text = subprocess.run(command + ['--format', 'text'],
                                  capture_output=True, text=True)
            self.assertEqual((default.returncode, explicit.returncode, text.returncode), (1, 1, 1))
            self.assertEqual(default.stdout, explicit.stdout)
            record = json.loads(default.stdout)
            for value in ('a' * 40, fx['run_id'], '2026-07-17', '260717', str(assurance)):
                self.assertIn(value, text.stdout)
            self.assertIn('Delivery authorization: BLOCKED', text.stdout)
            self.assertIn('Delivery evidence: UNPROVEN', text.stdout)
            for blocker in record['blockers']:
                self.assertIn(blocker, text.stdout)
            for name, artifact in record['artifact_hashes'].items():
                self.assertIn(f"{name}: {artifact['sha256']}", text.stdout)
            self.assertEqual(text.stderr, '')
            self.assertEqual(before, {p: p.read_bytes() for p in Path(tmp).iterdir()})
            for invalid in ('{', '{"artifact_hashes":[]}',
                            '{"artifact_hashes":{"english_report":null}}'):
                assurance.write_text(invalid, encoding='utf-8')
                malformed = subprocess.run(command + ['--format', 'text'],
                                           capture_output=True, text=True)
                self.assertEqual(malformed.returncode, 1)
                self.assertIn('Assurance unavailable or invalid', malformed.stdout)
                self.assertEqual(malformed.stderr, '')

    def test_missing_and_malformed_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'assurance.json'
            for content in (None, '{', '[]', '{}'):
                if content is not None:
                    path.write_text(content)
                status = operator_status(assurance=path, source_sha='a'*40,
                                         run_id='run', close_date='2026-07-17', report_token='260717')
                self.assertEqual(status['status'], 'BLOCKED')
                self.assertIn('Assurance unavailable or invalid', status['blockers'][0])

    def test_exact_package_tamper_identity_inventory_and_no_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fx = assurance_tests.ETFReleaseAssuranceTests()._fixture(root)
            assurance = root / 'assurance.json'
            record = build_release_assurance(
                source_sha=fx['source_sha'], github_run_id='123', run_id=fx['run_id'],
                requested_close_date=fx['close_date'], report_token=fx['token'],
                pricing_audit=fx['pricing'], runtime_state=fx['runtime'], run_manifest=fx['manifest'],
                portfolio_state=fx['portfolio'], trade_ledger=fx['ledger'],
                english_report=fx['en'], dutch_report=fx['nl'], output=assurance)
            args = dict(assurance=assurance, source_sha=fx['source_sha'], run_id=fx['run_id'],
                        close_date=fx['close_date'], report_token=fx['token'])
            before = {p: p.read_bytes() for p in root.iterdir()}
            status = operator_status(**args)
            self.assertEqual(status['status'], 'BLOCKED')
            self.assertEqual(status['authorization']['status'], 'BLOCKED')
            self.assertFalse(any('Artifact missing or changed' in b for b in status['blockers']))
            self.assertTrue(status['quality_checks'])
            self.assertEqual(before, {p: p.read_bytes() for p in root.iterdir()})
            wrong = operator_status(**{**args, 'run_id': 'other'})
            self.assertIn('identity mismatch', wrong['blockers'][0])
            altered = json.loads(assurance.read_text())
            altered['identity']['source_sha'] = 'b' * 40
            assurance.write_text(json.dumps(altered))
            disputed = operator_status(**{**args, 'source_sha': 'b' * 40})
            self.assertIn(
                'Assurance source SHA contradicts source identity evidence',
                disputed['blockers'],
            )
            assurance.write_text(json.dumps(record))
            fx['en'].write_text('changed')
            self.assertIn('Artifact missing or changed: english_report', operator_status(**args)['blockers'])
            fx['en'].unlink()
            self.assertIn('Artifact missing or changed: english_report', operator_status(**args)['blockers'])
            del record['artifact_hashes']['dutch_pdf']
            assurance.write_text(json.dumps(record))
            self.assertIn('Incomplete or unexpected package artifact inventory', operator_status(**args)['blockers'])


if __name__ == '__main__':
    unittest.main()
