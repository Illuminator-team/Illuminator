"""Compare e2e output CSVs with their expected versions.

Usage: python tests/compare_outputs.py OUT EXPECTED [OUT EXPECTED ...]

Columns, row count and the date column must match exactly. Numeric columns
may differ by at most ATOL, because the last float digit can vary between
CI runners. Other columns must match exactly. Exits 1 on any mismatch.
"""
import sys

import numpy as np
import pandas as pd

ATOL = 1e-9
MAX_ROWS_SHOWN = 5


def compare(out_path, expected_path):
    out = pd.read_csv(out_path, dtype={"date": str})
    expected = pd.read_csv(expected_path, dtype={"date": str})
    errors = []

    if list(out.columns) != list(expected.columns):
        errors.append(f"columns differ:\n  out:      {list(out.columns)}\n"
                      f"  expected: {list(expected.columns)}")
    if len(out) != len(expected):
        errors.append(f"row count differs: {len(out)} vs {len(expected)} expected")
    if errors:
        return errors

    for col in expected.columns:
        a, b = out[col], expected[col]
        numeric = (col != "date" and pd.api.types.is_numeric_dtype(a)
                   and pd.api.types.is_numeric_dtype(b))
        if numeric:
            same = np.isclose(a.to_numpy(dtype=float), b.to_numpy(dtype=float),
                              rtol=0, atol=ATOL, equal_nan=True)
        else:
            same = ((a == b) | (a.isna() & b.isna())).to_numpy()
        bad = np.flatnonzero(~same)
        if len(bad):
            kind = f"numeric, atol={ATOL}" if numeric else "exact"
            lines = [f"column '{col}' ({kind}): {len(bad)} row(s) differ"]
            av, bv = a.tolist(), b.tolist()  # plain Python values print cleanly
            for i in bad[:MAX_ROWS_SHOWN]:
                lines.append(f"  row {i} (date {expected['date'].iloc[i]}): "
                             f"{av[i]!r} vs {bv[i]!r} expected")
            errors.append("\n".join(lines))
    return errors


def main(args):
    if not args or len(args) % 2:
        sys.exit(__doc__)
    failed = False
    for out_path, expected_path in zip(args[::2], args[1::2]):
        errors = compare(out_path, expected_path)
        print(f"{'FAIL' if errors else 'OK'}: {out_path} vs {expected_path}")
        for e in errors:
            print(e)
        failed = failed or bool(errors)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
