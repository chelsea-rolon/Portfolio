import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


def normalize_color(value):
    s = (value or "").strip()

    # Unwrap repeated CSV-escaped quoting like '""#112233""' -> #112233.
    while len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1].strip()
    while len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        s = s[1:-1].strip()

    return s


def load_rows(csv_path, scene_filter=None):
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        original_fields = reader.fieldnames or []
        lower_to_original = {name.strip().lower(): name for name in original_fields}
        fieldnames = set(lower_to_original.keys())

        has_scene = "scene" in fieldnames
        rows = []

        # Format A: coordinate rows with columns c,r,color (and optional scene).
        required = {"c", "r", "color"}
        if required.issubset(fieldnames):
            for row in reader:
                scene = (row.get(lower_to_original.get("scene", "")) or "").strip()
                if scene_filter and has_scene and scene != scene_filter:
                    continue

                color = normalize_color(row.get(lower_to_original["color"]))
                if not color:
                    continue

                c = int((row.get(lower_to_original["c"]) or "").strip())
                r = int((row.get(lower_to_original["r"]) or "").strip())
                rows.append((c, r, color))
            return rows

        # Format B: grid matrix with r\c + c00..c49 (and optional scene column).
        grid_col_pattern = re.compile(r"^c(\d+)$")
        grid_columns = []
        for lower_name, original_name in lower_to_original.items():
            m = grid_col_pattern.match(lower_name)
            if m:
                grid_columns.append((int(m.group(1)), original_name))

        row_key = None
        for candidate in ("r\\c", "r/c", "row"):
            if candidate in fieldnames:
                row_key = lower_to_original[candidate]
                break

        if row_key and grid_columns:
            grid_columns.sort(key=lambda item: item[0])
            scene_key = lower_to_original.get("scene")

            for row in reader:
                scene = (row.get(scene_key) or "").strip() if scene_key else ""
                if scene_filter and has_scene and scene != scene_filter:
                    continue

                row_label = (row.get(row_key) or "").strip().lower()
                if row_label.startswith("r"):
                    row_label = row_label[1:]
                if not row_label.isdigit():
                    continue
                r = int(row_label)

                for c, col_name in grid_columns:
                    color = normalize_color(row.get(col_name))
                    if color:
                        rows.append((c, r, color))
            return rows

        raise ValueError(
            "CSV format not recognized. Use columns c,r,color (optional scene) "
            "or grid format with r\\c and c00..c49 (optional scene)."
        )


def render_grouped(rows):
    by_color = defaultdict(list)
    for c, r, color in rows:
        by_color[color].append((c, r))

    lines = ["# Generated from editable CSV", "self.canvas.delete(\"all\")"]
    for color in sorted(by_color.keys()):
        coords = sorted(by_color[color], key=lambda p: (p[1], p[0]))
        lines.append(f"for c, r in {coords}:")
        lines.append(f"    self._px(c, r, \"{color}\")")
    return "\n".join(lines) + "\n"


def render_raw(rows):
    rows = sorted(rows, key=lambda p: (p[1], p[0], p[2]))
    lines = ["# Generated from editable CSV", "self.canvas.delete(\"all\")"]
    for c, r, color in rows:
        lines.append(f"self._px({c}, {r}, \"{color}\")")
    return "\n".join(lines) + "\n"


def update_method_body(py_path, method_name, generated_code):
    text = py_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    method_line = None
    method_indent = 0
    needle = f"def {method_name}("

    for i, line in enumerate(lines):
        stripped = line.lstrip(" ")
        if stripped.startswith(needle):
            method_line = i
            method_indent = len(line) - len(stripped)
            break

    if method_line is None:
        raise ValueError(f"Method not found: {method_name}")

    end = len(lines)
    for j in range(method_line + 1, len(lines)):
        stripped = lines[j].strip()
        if not stripped:
            continue
        indent = len(lines[j]) - len(lines[j].lstrip(" "))
        if indent <= method_indent:
            end = j
            break

    body_indent = " " * (method_indent + 4)
    generated_lines = generated_code.rstrip("\n").split("\n")
    new_body = []
    for gl in generated_lines:
        if gl:
            new_body.append(f"{body_indent}{gl}\n")
        else:
            new_body.append("\n")

    new_lines = lines[: method_line + 1] + new_body + lines[end:]
    py_path.write_text("".join(new_lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Convert editable pixel CSVs into Python drawing code."
    )
    parser.add_argument("input", help="Path to editable CSV file")
    parser.add_argument(
        "--scene",
        default=None,
        help="Scene name filter when using editable_all_backgrounds.csv",
    )
    parser.add_argument(
        "--mode",
        choices=["grouped", "raw"],
        default="grouped",
        help="Output grouped loops by color or one _px call per row",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output .py file path; otherwise prints to console",
    )
    parser.add_argument(
        "--apply-file",
        default=None,
        help="Optional Python file to update in place",
    )
    parser.add_argument(
        "--method",
        default=None,
        help="Method name to replace when using --apply-file (example: _draw_dark_forest)",
    )

    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    rows = load_rows(input_path, scene_filter=args.scene)
    if not rows:
        raise ValueError("No drawable rows found. Check CSV values and scene filter.")

    code = render_grouped(rows) if args.mode == "grouped" else render_raw(rows)

    if args.output:
        out = Path(args.output)
        out.write_text(code, encoding="utf-8")
        print(f"Wrote: {out}")

    if args.apply_file:
        if not args.method:
            raise ValueError("--method is required when using --apply-file")
        py_path = Path(args.apply_file)
        if not py_path.exists():
            raise FileNotFoundError(f"Python file not found: {py_path}")
        update_method_body(py_path, args.method, code)
        print(f"Updated {args.method} in: {py_path}")

    if not args.output and not args.apply_file:
        print(code)


if __name__ == "__main__":
    main()
