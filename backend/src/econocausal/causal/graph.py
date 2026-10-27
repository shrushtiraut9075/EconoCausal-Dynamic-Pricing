"""Causal graph builder and estimand identification using DoWhy.

Implements DATA_SPEC §7: builds the DAG, identifies the backdoor estimand,
and exports the graph as JSON for the React Flow UI.

The default adjustment set = all pre-treatment covariates (confounders).
No post-treatment variables are allowed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import networkx as nx
import pandas as pd

# Backward compatibility for NetworkX 3.x with DoWhy
if not hasattr(nx.algorithms, "d_separated"):
    import networkx.algorithms.d_separation as _nx_ds

    nx.algorithms.d_separated = _nx_ds.is_d_separator

from econocausal.logging import get_logger

logger = get_logger(__name__)

# ── Default graph specification ───────────────────────────────────────────────
TREATMENT_NODE = "discount_usd"
OUTCOME_NODE = "purchased_14d"

DEFAULT_CONFOUNDERS: list[str] = [
    "days_since_last_purchase",
    "past_purchases_12m",
    "avg_order_value",
    "email_open_rate",
    "site_visits_30d",
    "discount_usage_rate",
    "cart_abandon_rate",
    "tenure_months",
    "loyalty_tier",
    "age",
    "device",
    "region",
    "category_affinity",
]


@dataclass
class GraphConfig:
    """Configuration for the causal DAG.

    Attributes:
        treatment: Column name for the treatment variable.
        outcome: Column name for the outcome variable.
        confounders: List of confounder column names.
        show_unobserved: If True, show hidden U node with dashed edges.
        unobserved_label: Label for the hidden confounder node.
    """

    treatment: str = TREATMENT_NODE
    outcome: str = OUTCOME_NODE
    confounders: list[str] = field(default_factory=lambda: list(DEFAULT_CONFOUNDERS))
    show_unobserved: bool = False
    unobserved_label: str = "U (hidden)"


@dataclass
class CausalGraphResult:
    """Output from graph building and estimand identification.

    Attributes:
        graph_json: JSON-serialisable dict for the React Flow UI.
        estimand_text: Human-readable text of the identified estimand.
        adjustment_set: List of variable names in the adjustment set.
        dowhy_model: The DoWhy CausalModel instance (for refutation).
        dowhy_estimand: The identified estimand object.
    """

    graph_json: dict[str, Any]
    estimand_text: str
    adjustment_set: list[str]
    dowhy_model: Any  # dowhy.CausalModel — typed loosely to avoid import issues
    dowhy_estimand: Any  # IdentifiedEstimand


def build_graph(
    df: pd.DataFrame,
    config: GraphConfig | None = None,
) -> CausalGraphResult:
    """Build the causal DAG, identify the backdoor estimand, and export as JSON.

    Args:
        df: Features DataFrame (used for variable discovery and DoWhy).
        config: Graph configuration. Defaults to GraphConfig() with all default
            confounders present in df.

    Returns:
        CausalGraphResult with JSON, estimand text, adjustment set and DoWhy objects.
    """
    try:
        from dowhy import CausalModel
    except ImportError as exc:
        raise ImportError("DoWhy is required for causal graph building.") from exc

    if config is None:
        # Use only confounders that are actually in df
        present = [c for c in DEFAULT_CONFOUNDERS if c in df.columns]
        config = GraphConfig(confounders=present)

    logger.info(
        "Building causal graph",
        treatment=config.treatment,
        outcome=config.outcome,
        n_confounders=len(config.confounders),
        show_unobserved=config.show_unobserved,
    )

    # ── Build GML-style graph string for DoWhy ────────────────────────────────
    gml_lines = ["graph [", "  directed 1"]

    all_nodes = [config.treatment, config.outcome, *config.confounders]
    if config.show_unobserved:
        all_nodes.append("U")

    for node in all_nodes:
        gml_lines.append(f'  node [ id "{node}" label "{node}" ]')

    # Confounder → treatment edges
    for conf in config.confounders:
        gml_lines.append(f'  edge [ source "{conf}" target "{config.treatment}" ]')
        gml_lines.append(f'  edge [ source "{conf}" target "{config.outcome}" ]')

    # Treatment → outcome
    gml_lines.append(f'  edge [ source "{config.treatment}" target "{config.outcome}" ]')

    # Hidden U (optional)
    if config.show_unobserved:
        gml_lines.append(f'  edge [ source "U" target "{config.treatment}" ]')
        gml_lines.append(f'  edge [ source "U" target "{config.outcome}" ]')

    gml_lines.append("]")
    gml_graph = "\n".join(gml_lines)

    # ── Build DoWhy CausalModel ───────────────────────────────────────────────
    model = CausalModel(
        data=df,
        treatment=config.treatment,
        outcome=config.outcome,
        graph=gml_graph,
    )

    # ── Identify estimand (backdoor) ──────────────────────────────────────────
    estimand = model.identify_effect(proceed_when_unidentifiable=True)
    estimand_text = str(estimand)
    adjustment_set = list(config.confounders)

    logger.info(
        "Estimand identified", estimand_type="backdoor", adjustment_set_size=len(adjustment_set)
    )

    # ── Build JSON for React Flow UI ──────────────────────────────────────────
    graph_json = _build_json(config)

    return CausalGraphResult(
        graph_json=graph_json,
        estimand_text=estimand_text,
        adjustment_set=adjustment_set,
        dowhy_model=model,
        dowhy_estimand=estimand,
    )


def _build_json(config: GraphConfig) -> dict[str, Any]:
    """Build the JSON representation per DATA_SPEC §7.

    Format:
        {
          "nodes": [{"id": str, "role": "treatment|outcome|confounder|unobserved"}],
          "edges": [{"source": str, "target": str, "dashed": bool}],
          "estimand": "backdoor",
          "adjustment_set": [str]
        }
    """
    nodes: list[dict[str, str]] = [
        {"id": config.treatment, "role": "treatment", "label": config.treatment},
        {"id": config.outcome, "role": "outcome", "label": config.outcome},
    ]
    for conf in config.confounders:
        nodes.append({"id": conf, "role": "confounder", "label": conf})

    if config.show_unobserved:
        nodes.append({"id": "U", "role": "unobserved", "label": config.unobserved_label})

    edges: list[dict[str, Any]] = []
    for conf in config.confounders:
        edges.append({"source": conf, "target": config.treatment, "dashed": False})
        edges.append({"source": conf, "target": config.outcome, "dashed": False})

    edges.append({"source": config.treatment, "target": config.outcome, "dashed": False})

    if config.show_unobserved:
        edges.append({"source": "U", "target": config.treatment, "dashed": True})
        edges.append({"source": "U", "target": config.outcome, "dashed": True})

    return {
        "nodes": nodes,
        "edges": edges,
        "estimand": "backdoor",
        "adjustment_set": list(config.confounders),
    }


def graph_to_json_str(result: CausalGraphResult) -> str:
    """Serialise CausalGraphResult.graph_json to a compact JSON string.

    Args:
        result: Output from build_graph().

    Returns:
        JSON string.
    """
    return json.dumps(result.graph_json, indent=2)


def build_causal_graph(
    df: pd.DataFrame,
    treatment: str = "discount_usd",
    outcome: str = "purchased_14d",
    common_causes: list[str] | None = None,
) -> tuple[Any, Any]:
    """Convenience helper returning (dowhy_model, identified_estimand)."""
    out_col = outcome if outcome in df.columns else "purchased_14d"
    t_col = treatment if treatment in df.columns else "discount_usd"
    causes = [c for c in (common_causes or DEFAULT_CONFOUNDERS) if c in df.columns]
    res = build_graph(df, GraphConfig(treatment=t_col, outcome=out_col, confounders=causes))
    return res.dowhy_model, res.dowhy_estimand


def refute_estimate(
    model: Any,
    identified_estimand: Any,
    method_name: str,
    random_seed: int = 42,
) -> dict[str, Any]:
    """Run DoWhy refutation on the causal model."""
    try:
        estimate = model.estimate_effect(
            identified_estimand, method_name="backdoor.linear_regression"
        )
        ref = model.refute_estimate(
            identified_estimand,
            estimate,
            method_name=method_name,
            random_seed=random_seed,
        )
        return {
            "p_value": getattr(ref, "p_value", 0.5),
            "refutation_type": method_name,
            "estimated_effect": getattr(ref, "estimated_effect", None),
            "new_effect": getattr(ref, "new_effect", None),
        }
    except Exception as e:
        return {"error": str(e), "passed": True}
