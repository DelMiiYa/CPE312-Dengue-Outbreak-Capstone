"""Tests for the self-contained runnable Jupyter notebook (T10).

Verifies that notebooks/capstone_dengue.ipynb:
1. Exists and is valid nbformat v4 JSON.
2. Has zero cell execution errors.
3. Contains all required R1-R7 sections, framing questions, and inline figures (>= 4).
4. Strictly matches results/metrics.json and passes automated consistency audit.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import nbformat


@pytest.fixture(scope="module")
def notebook_data() -> dict:
    nb_path = Path("notebooks/capstone_dengue.ipynb")
    assert nb_path.exists(), f"Notebook not found at {nb_path}. Run build_notebook.py first."
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    return nb


def test_notebook_file_exists():
    nb_path = Path("notebooks/capstone_dengue.ipynb")
    assert nb_path.exists()
    assert nb_path.stat().st_size > 50_000, "Notebook size is too small; figures may be missing."


def test_valid_nbformat_v4(notebook_data):
    assert notebook_data.get("nbformat") == 4
    assert notebook_data.get("nbformat_minor", 0) >= 0
    assert "cells" in notebook_data
    assert isinstance(notebook_data["cells"], list)
    # Validate against official nbformat schema
    nbformat.validate(notebook_data)


def test_cell_counts_and_ids(notebook_data):
    cells = notebook_data["cells"]
    code_cells = [c for c in cells if c.get("cell_type") == "code"]
    md_cells = [c for c in cells if c.get("cell_type") == "markdown"]

    assert len(cells) >= 15, f"Expected at least 15 cells, got {len(cells)}"
    assert len(code_cells) >= 10, f"Expected at least 10 code cells, got {len(code_cells)}"
    assert len(md_cells) >= 6, f"Expected at least 6 markdown cells, got {len(md_cells)}"

    # Check cell ids are defined and unique
    cell_ids = [c.get("id") for c in cells if "id" in c]
    assert len(cell_ids) == len(cells), "Every cell must have an 'id' attribute."
    assert len(set(cell_ids)) == len(cells), "Cell IDs must be unique."


def test_zero_execution_errors(notebook_data):
    code_cells = [c for c in notebook_data["cells"] if c.get("cell_type") == "code"]
    errors = []
    for idx, cell in enumerate(code_cells):
        outputs = cell.get("outputs", [])
        for out in outputs:
            if out.get("output_type") == "error":
                errors.append((idx, out.get("ename"), out.get("evalue")))

    assert len(errors) == 0, f"Encountered cell execution errors: {errors}"


def test_inline_figures_count(notebook_data):
    code_cells = [c for c in notebook_data["cells"] if c.get("cell_type") == "code"]
    png_outputs = []
    for cell in code_cells:
        for out in cell.get("outputs", []):
            if "image/png" in out.get("data", {}):
                png_outputs.append(out["data"]["image/png"])

    # Brief requires at least 4 inline PNGs; notebook produces 7
    assert len(png_outputs) >= 4, f"Expected at least 4 inline PNG plots, found {len(png_outputs)}"
    for b64_img in png_outputs:
        assert len(b64_img) > 1000, "Base64 image data appears corrupted or empty."


def test_all_crisp_dm_sections_present(notebook_data):
    md_text = "\n".join("".join(c.get("source", [])) for c in notebook_data["cells"] if c.get("cell_type") == "markdown")

    required_keywords = [
        "เดือนหน้าไข้เลือดออกระบาดไหม",
        "Section 1: Problem Statement & R1",
        "Section 2: R2 Data Understanding",
        "Section 3: R3 Exploratory Data Analysis",
        "Section 4: R2/R4 Feature Engineering",
        "Section 5: R4 Modeling",
        "Section 6: R5 Evaluation & Quantitative Error Analysis",
        "Section 7: R6 Deployment",
        "Section 8: R7 AI-Use Log Summary",
        "OpenDengue",
        "Open-Meteo",
        "CC BY 4.0",
        "Two-Tier",
    ]

    for kw in required_keywords:
        assert kw in md_text, f"Missing required section or keyword: '{kw}'"


def test_notebook_metrics_consistency(notebook_data):
    all_stdout = "\n".join(
        "".join(out.get("text", []))
        for cell in notebook_data["cells"]
        if cell.get("cell_type") == "code"
        for out in cell.get("outputs", [])
        if out.get("output_type") == "stream" and out.get("name") == "stdout"
    )

    # Verify key verified numbers from metrics.json appear in stdout
    with open("results/metrics.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)

    hgb_test = metrics["models"]["hist_gradient_boosting"]["metrics"]["test"]
    assert f"{hgb_test['recall']:.4f}" in all_stdout, "HistGradientBoosting recall not found in notebook stdout"
    assert "0.8827" in all_stdout
    assert "346" in all_stdout  # TP
    assert "295" in all_stdout  # FP
    assert "46" in all_stdout   # FN
    assert "392" in all_stdout  # Support pos

    # Verify audit completion confirmation message
    assert "All 35+ numerical consistency assertions PASSED." in all_stdout


def test_standalone_colab_gdrive_bootstrap(notebook_data):
    """Verify Cell 1 downloads the public Google Drive bundle cleanly when run standalone in Colab."""
    code_cells = [c for c in notebook_data["cells"] if c.get("cell_type") == "code"]
    cell1_src = "".join(code_cells[0].get("source", []))

    assert "1SLcdp1ovK76mL28IG_RNG6TaGjrfGLKx" in cell1_src
    assert "zipfile.ZipFile" in cell1_src
    assert "REQUIRED_FILES" in cell1_src
    assert "github.com/Antigravity-Projects/DS_capstone.git" not in cell1_src
