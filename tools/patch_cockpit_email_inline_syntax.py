from pathlib import Path

path = Path("runtime/cockpit_email_safe_surface.py")
text = path.read_text(encoding="utf-8")

old_spark = '''def _sparkline_text(points: Iterable[tuple[str, float]]) -> str:
    values = [float(value) for _, value in points]
    if not values:
        return "—"
    if len(values) > 44:
        step = max(1, len(values) // 44)
        values = values[::step]
        if values[-1] != list(points)[-1][1]:
            values.append(float(list(points)[-1][1]))
'''
new_spark = '''def _sparkline_text(points: Iterable[tuple[str, float]]) -> str:
    point_list = list(points)
    values = [float(value) for _, value in point_list]
    if not values:
        return "—"
    if len(values) > 44:
        step = max(1, len(values) // 44)
        values = values[::step]
        final_value = float(point_list[-1][1])
        if values[-1] != final_value:
            values.append(final_value)
'''
if old_spark not in text:
    raise SystemExit("sparkline anchor missing")
text = text.replace(old_spark, new_spark, 1)

old_rows = '''    evidence_rows_html = "".join(
        f"<tr>{evidence_cells[index]}{evidence_cells[index + 1] if index + 1 < len(evidence_cells) else '<td style=\\\"width:50%\\\"></td>'}</tr>"
        for index in range(0, len(evidence_cells), 2)
    )
'''
new_rows = '''    empty_evidence_cell = '<td style="width:50%"></td>'
    evidence_rows_html = "".join(
        "<tr>"
        + evidence_cells[index]
        + (evidence_cells[index + 1] if index + 1 < len(evidence_cells) else empty_evidence_cell)
        + "</tr>"
        for index in range(0, len(evidence_cells), 2)
    )
'''
if old_rows not in text:
    raise SystemExit("evidence row anchor missing")
text = text.replace(old_rows, new_rows, 1)

path.write_text(text, encoding="utf-8")
