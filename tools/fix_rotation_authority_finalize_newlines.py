from pathlib import Path

path = Path("tests/test_etf_rotation_state_authority.py")
text = path.read_text(encoding="utf-8")
marker = r"\n\n\ndef test_average_entry_reconstructed_from_execution_history"
if marker not in text:
    raise SystemExit("staged rotation test marker not found")
prefix, tail = text.split(marker, 1)
text = prefix + (marker + tail).replace(r"\n", "\n")
path.write_text(text, encoding="utf-8")
print("ROTATION_AUTHORITY_TEST_NEWLINES_OK")
