"""test_recommendations.py — Unit tests for T09 policy recommendations and trade-offs.

Verifies:
1. results/policy_analysis.json existence, schema, and exact numerical consistency.
2. Operational policies (No-Alert, Blanket, Persistence, Single-Threshold ML, Two-Tier ML).
3. Two-Tier alert protocol partition (Green, Yellow, Red) and outbreak capture.
4. Cost sensitivity calculations across R in {3, 5, 10, 15} and proof of ML dominance.
5. Dynamic subperiod adaptation (Normal 2018-2019 vs COVID 2020-2022).
6. Publication figure results/figures/r6_threshold_policy.png (300 DPI, > 20 KB).
7. Deployment guide results/recommendations.md (required sections and 4 limitations).
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from PIL import Image


@pytest.fixture(scope="module")
def policy_data() -> dict:
    json_path = Path("results/policy_analysis.json")
    assert json_path.exists(), f"Missing policy analysis JSON at {json_path}"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def recommendations_text() -> str:
    md_path = Path("results/recommendations.md")
    assert md_path.exists(), f"Missing recommendations markdown at {md_path}"
    with open(md_path, "r", encoding="utf-8") as f:
        return f.read()


class TestPolicyAnalysisJSON:
    def test_top_level_keys(self, policy_data: dict) -> None:
        required_keys = [
            "metadata",
            "policies_test",
            "policies_val",
            "two_tier_test",
            "two_tier_val",
            "subperiods_test",
            "threshold_sweep",
        ]
        for key in required_keys:
            assert key in policy_data, f"Missing required key: {key}"

    def test_metadata_consistency(self, policy_data: dict) -> None:
        meta = policy_data["metadata"]
        assert meta["provinces"] == 77
        assert meta["test_province_months"] == 4620
        assert meta["test_outbreaks"] == 392
        assert meta["val_province_months"] == 1848
        assert meta["val_outbreaks"] == 70
        assert meta["r_sensitivity_values"] == [3, 5, 10, 15]
        assert meta["val_tuned_threshold"] == 0.49

    def test_policies_test_keys(self, policy_data: dict) -> None:
        policies = policy_data["policies_test"]
        required_policies = [
            "no_alert",
            "majority_class",
            "blanket_rainy_season",
            "reactive_persistence",
            "single_threshold_hgb_0.49",
            "two_tier_ml",
            "two_tier_ml_weighted",
            "two_tier_ml_standard",
        ]
        for pol in required_policies:
            assert pol in policies, f"Missing policy: {pol}"


class TestOperationalPoliciesTestMetrics:
    def test_no_alert_policy(self, policy_data: dict) -> None:
        pol = policy_data["policies_test"]["no_alert"]
        assert pol["total_alerts"] == 0
        assert pol["alerts_per_province_per_year"] == 0.0
        assert pol["tp"] == 0
        assert pol["fn"] == 392
        assert pol["recall"] == 0.0
        assert pol["cost_by_r"]["5"] == 1960.0
        assert pol["cost_by_r"]["10"] == 3920.0

    def test_blanket_rainy_season(self, policy_data: dict) -> None:
        pol = policy_data["policies_test"]["blanket_rainy_season"]
        assert pol["total_alerts"] == 2310
        assert pol["alerts_per_province_per_year"] == 6.0
        assert pol["pct_province_months"] == 50.0
        assert pol["tp"] == 346
        assert pol["fn"] == 46
        assert pol["fp"] == 1964
        assert pytest.approx(pol["recall"], abs=1e-3) == 0.8827
        assert pytest.approx(pol["precision"], abs=1e-3) == 0.1498
        assert pol["cost_by_r"]["5"] == 2540.0
        assert pol["cost_by_r"]["10"] == 2770.0

    def test_reactive_persistence(self, policy_data: dict) -> None:
        pol = policy_data["policies_test"]["reactive_persistence"]
        assert pol["total_alerts"] == 386
        assert pol["tp"] == 244
        assert pol["fn"] == 148
        assert pol["fp"] == 142
        assert pytest.approx(pol["recall"], abs=1e-3) == 0.6224
        assert pytest.approx(pol["precision"], abs=1e-3) == 0.6321
        assert pol["cost_by_r"]["5"] == 1126.0
        assert pol["cost_by_r"]["10"] == 1866.0

    def test_single_threshold_ml_049(self, policy_data: dict) -> None:
        pol = policy_data["policies_test"]["single_threshold_hgb_0.49"]
        assert pol["total_alerts"] == 641
        assert pytest.approx(pol["alerts_per_province_per_year"], abs=1e-2) == 1.66
        assert pytest.approx(pol["pct_province_months"], abs=1e-2) == 13.87
        assert pol["tp"] == 346
        assert pol["fn"] == 46
        assert pol["fp"] == 295
        assert pytest.approx(pol["recall"], abs=1e-3) == 0.8827
        assert pytest.approx(pol["precision"], abs=1e-3) == 0.5398
        assert pol["cost_by_r"]["5"] == 871.0
        assert pol["cost_by_r"]["10"] == 1101.0

    def test_two_tier_ml_test(self, policy_data: dict) -> None:
        pol = policy_data["policies_test"]["two_tier_ml_weighted"]
        assert pol["total_alerts"] == 749
        assert pol["tp"] == 357
        assert pol["fn"] == 35
        assert pol["fp"] == 392
        assert pytest.approx(pol["recall"], abs=1e-3) == 0.9107
        assert pytest.approx(pol["precision"], abs=1e-3) == 0.4766
        assert pytest.approx(pol["cost_by_r"]["5"], abs=1e-1) == 768.6
        assert pytest.approx(pol["cost_by_r"]["10"], abs=1e-1) == 943.6


class TestTwoTierProtocolStructure:
    def test_two_tier_test_partition(self, policy_data: dict) -> None:
        tt = policy_data["two_tier_test"]
        assert tt["threshold_yellow"] == 0.35
        assert tt["threshold_red"] == 0.65

        g = tt["green"]
        y = tt["yellow"]
        r = tt["red"]

        # Exact row counts sum to 4620
        assert g["count"] == 3871
        assert y["count"] == 222
        assert r["count"] == 527
        assert g["count"] + y["count"] + r["count"] == 4620

        # Exact outbreak counts sum to 392
        assert g["outbreaks"] == 35
        assert y["outbreaks"] == 38
        assert r["outbreaks"] == 319
        assert g["outbreaks"] + y["outbreaks"] + r["outbreaks"] == 392

        # Risk rates
        assert pytest.approx(g["outbreak_rate"], abs=1e-3) == 0.0090
        assert pytest.approx(y["outbreak_rate"], abs=1e-3) == 0.1712
        assert pytest.approx(r["outbreak_rate"], abs=1e-3) == 0.6053

        # Outbreak shares
        assert pytest.approx(g["share_of_all_outbreaks"], abs=1e-3) == 0.0893
        assert pytest.approx(y["share_of_all_outbreaks"], abs=1e-3) == 0.0969
        assert pytest.approx(r["share_of_all_outbreaks"], abs=1e-3) == 0.8138

    def test_two_tier_val_consistency(self, policy_data: dict) -> None:
        tt = policy_data["two_tier_val"]
        g = tt["green"]
        y = tt["yellow"]
        r = tt["red"]

        assert g["count"] + y["count"] + r["count"] == 1848
        assert g["outbreaks"] + y["outbreaks"] + r["outbreaks"] == 70
        assert g["outbreaks"] == 6
        assert y["outbreaks"] == 12
        assert r["outbreaks"] == 52
        assert pytest.approx(tt["overall_alert_zone"]["recall"], abs=1e-3) == 0.9143


class TestCostSensitivityAndDominance:
    def test_cost_calculation_correctness(self, policy_data: dict) -> None:
        policies = policy_data["policies_test"]
        for r_str in ["3", "5", "10", "15"]:
            r_val = float(r_str)
            # Single threshold ML: Cost = 641 + 46 * R
            expected_ml = 641.0 + 46.0 * r_val
            assert pytest.approx(policies["single_threshold_hgb_0.49"]["cost_by_r"][r_str], abs=1e-2) == expected_ml

            # Blanket: Cost = 2310 + 46 * R
            expected_blanket = 2310.0 + 46.0 * r_val
            assert pytest.approx(policies["blanket_rainy_season"]["cost_by_r"][r_str], abs=1e-2) == expected_blanket

            # Persistence: Cost = 386 + 148 * R
            expected_pers = 386.0 + 148.0 * r_val
            assert pytest.approx(policies["reactive_persistence"]["cost_by_r"][r_str], abs=1e-2) == expected_pers

            # Two-Tier Weighted: Cost = 593.6 + 35 * R
            expected_two_w = 593.6 + 35.0 * r_val
            assert pytest.approx(policies["two_tier_ml_weighted"]["cost_by_r"][r_str], abs=1e-2) == expected_two_w

    def test_ml_dominance_for_r_gte_3(self, policy_data: dict) -> None:
        policies = policy_data["policies_test"]
        for r_str in ["3", "5", "10", "15"]:
            c_two_w = policies["two_tier_ml_weighted"]["cost_by_r"][r_str]
            c_hgb = policies["single_threshold_hgb_0.49"]["cost_by_r"][r_str]
            c_blanket = policies["blanket_rainy_season"]["cost_by_r"][r_str]
            c_pers = policies["reactive_persistence"]["cost_by_r"][r_str]
            c_no_alert = policies["no_alert"]["cost_by_r"][r_str]

            # Two-Tier Weighted dominates every baseline for all R >= 3
            assert c_two_w < c_blanket, f"Failed: c_two_w ({c_two_w}) >= c_blanket ({c_blanket}) at R={r_str}"
            assert c_two_w < c_pers, f"Failed: c_two_w ({c_two_w}) >= c_pers ({c_pers}) at R={r_str}"
            assert c_two_w < c_no_alert, f"Failed: c_two_w ({c_two_w}) >= c_no_alert ({c_no_alert}) at R={r_str}"

            # Single ML also dominates Blanket and No-Alert, and beats Persistence at R >= 3
            assert c_hgb < c_blanket
            assert c_hgb < c_pers
            assert c_hgb < c_no_alert


class TestSubperiodsAdaptation:
    def test_subperiod_scaling(self, policy_data: dict) -> None:
        sub = policy_data["subperiods_test"]
        norm = sub["normal"]["policies"]["single_threshold_hgb_0.49"]
        covid = sub["covid"]["policies"]["single_threshold_hgb_0.49"]

        # Normal alerts/yr (445 / (77 * 2) = 2.89) vs COVID (196 / (77 * 3) = 0.85)
        assert norm["alerts_per_province_per_year"] > covid["alerts_per_province_per_year"]
        # Both achieve high recall
        assert norm["recall"] > 0.88
        assert covid["recall"] > 0.85


class TestPublicationFigureAndReport:
    def test_figure_file(self) -> None:
        fig_path = Path("results/figures/r6_threshold_policy.png")
        assert fig_path.exists(), f"Missing figure at {fig_path}"
        assert fig_path.stat().st_size > 20_000, "Figure size too small (< 20 KB)"

        with Image.open(fig_path) as im:
            width, height = im.size
            assert width >= 2000, f"Image width {width} px too small for 300 DPI"
            assert height >= 1000, f"Image height {height} px too small for 300 DPI"

    def test_recommendations_markdown_content(self, recommendations_text: str) -> None:
        # Minimum size check
        assert len(recommendations_text) > 2000

        # Required sections
        required_phrases = [
            "Two-Tier Early Warning Protocol",
            "Green (Routine)",
            "Yellow (Tier-1 Watch)",
            "Red (Tier-2 High Alert)",
            "Workload & Operational Policy Comparison",
            "Blanket Rainy-Season",
            "Reactive Persistence",
            "Parametric Cost Sensitivity Analysis",
            "Dynamic Workload Adaptation",
            "Practical Limitations: What the Data Cannot Prove",
            "Observational Surveillance Data vs. Causal Treatment Effect",
            "Spatial Resolution: Admin1 Province vs. Village/Subdistrict",
            "Unobserved Viral Serotypes, Herd Immunity, and Human Mobility",
            "Grid Reanalysis Weather vs. Urban Microclimates",
            "Implementation Checklist for สสจ.",
        ]
        for phrase in required_phrases:
            assert phrase.lower() in recommendations_text.lower(), f"Missing required phrase in markdown: {phrase}"
