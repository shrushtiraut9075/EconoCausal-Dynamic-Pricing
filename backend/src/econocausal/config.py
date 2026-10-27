"""EconoCausal global configuration via pydantic-settings.

All values can be overridden via environment variables or a .env file.
No magic numbers — every constant lives here or in config YAML.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PRE_TREATMENT_COVARIATES: list[str] = [
    "age",
    "tenure_months",
    "past_purchases_12m",
    "avg_order_value",
    "days_since_last_purchase",
    "site_visits_30d",
    "email_open_rate",
    "discount_usage_rate",
    "cart_abandon_rate",
    "loyalty_tier",
    "device",
    "region",
    "category_affinity",
]


class Settings(BaseSettings):
    """Application-wide settings loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Paths ────────────────────────────────────────────────────────────────
    project_root: Path = Field(default=Path("."), description="Project root directory")
    data_dir: Path = Field(default=Path("data"), description="Root data directory")
    artifacts_dir: Path = Field(default=Path("artifacts"), description="Model/allocation artifacts")
    reports_dir: Path = Field(default=Path("reports"), description="Auto-generated reports")

    # ── API ──────────────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_reload: bool = Field(default=True)
    api_cors_origins: list[str] = Field(default=["http://localhost:5173", "http://localhost:3000"])
    max_upload_size_mb: int = Field(default=50, description="Max CSV upload size in MB")

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    log_format: Literal["console", "json"] = Field(default="console")

    # ── Model defaults ────────────────────────────────────────────────────────
    default_seed: int = Field(default=42)
    default_n_estimators: int = Field(default=200, description="CausalForestDML n_estimators")
    default_cv_folds: int = Field(default=5, description="Cross-fitting folds (K)")
    default_margin_rate: float = Field(default=0.40, description="Gross margin rate")
    default_budget: float = Field(default=5000.0, description="Default marketing budget $")

    # ── Simulator ────────────────────────────────────────────────────────────
    sim_levels: tuple[int, ...] = Field(
        default=(0, 5, 10, 20), description="Discount levels in USD"
    )
    sim_n_full: int = Field(default=100_000, description="Full training population size")
    sim_n_demo: int = Field(default=20_000, description="Demo/CI preset size")
    sim_n_rct: int = Field(default=20_000, description="Randomised holdout size")
    sim_train_frac: float = Field(default=0.70, description="Train fraction of confounded data")
    sim_valid_frac: float = Field(default=0.10, description="Valid fraction")
    sim_test_obs_frac: float = Field(default=0.20, description="Test (confounded) fraction")
    stability_seeds: tuple[int, ...] = Field(
        default=(11, 22, 33, 44, 55), description="Seeds for stability study"
    )

    # ── Propensity / overlap ──────────────────────────────────────────────────
    propensity_clip_low: float = Field(default=0.02)
    propensity_clip_high: float = Field(default=0.98)
    overlap_warn_frac: float = Field(
        default=0.10, description="WARN if > this fraction outside clip"
    )
    overlap_fail_frac: float = Field(
        default=0.25, description="FAIL if > this fraction outside clip"
    )

    # ── Evaluation thresholds ─────────────────────────────────────────────────
    ate_error_target: float = Field(default=0.10, description="ATE relative error ≤ 10%")
    pehe_improvement_target: float = Field(
        default=0.25, description="PEHE improvement vs S-learner ≥ 25%"
    )
    spearman_target: float = Field(default=0.60, description="Spearman ρ ≥ 0.60")
    profit_vs_blanket_target: float = Field(default=0.25, description="Profit vs blanket ≥ +25%")

    # ── Drift detection ───────────────────────────────────────────────────────
    psi_green: float = Field(default=0.10)
    psi_amber: float = Field(default=0.25)

    # ── Refutation ────────────────────────────────────────────────────────────
    refute_n_simulations: int = Field(default=30, description="DoWhy refuter num_simulations")
    refute_max_rows: int = Field(default=20_000, description="Max rows per refuter run")

    # ── Optimiser ────────────────────────────────────────────────────────────
    milp_max_customers: int = Field(default=5_000, description="Use MILP for N ≤ this")

    @field_validator("data_dir", "artifacts_dir", "reports_dir", mode="before")
    @classmethod
    def make_path(cls, v: str | Path) -> Path:
        """Ensure paths are Path objects."""
        return Path(v)

    @property
    def processed_dir(self) -> Path:
        """Processed Parquet data directory."""
        return self.data_dir / "processed"

    @property
    def models_dir(self) -> Path:
        """Model artifacts directory."""
        return self.artifacts_dir / "models"

    @property
    def allocations_dir(self) -> Path:
        """Allocation artifacts directory."""
        return self.artifacts_dir / "allocations"

    def ensure_dirs(self) -> None:
        """Create all required directories if they don't exist."""
        for d in [
            self.processed_dir,
            self.models_dir,
            self.allocations_dir,
            self.reports_dir / "figures",
        ]:
            d.mkdir(parents=True, exist_ok=True)


# Singleton settings instance
settings = Settings()
