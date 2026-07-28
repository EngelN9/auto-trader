"""Typed configuration contracts for the Milestone 0 skeleton."""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FrozenModel(BaseModel):
    """Forbid undeclared configuration and mutation after validation."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class EnvironmentMode(StrEnum):
    RESEARCH = "research"
    BACKTEST = "backtest"
    REPLAY = "replay"
    PAPER = "paper"
    SHADOW = "shadow"
    CANARY = "canary"
    LIVE = "live"


class SystemSettings(FrozenModel):
    mode: EnvironmentMode
    timezone: str
    deterministic: bool
    live_enabled: bool
    startup_permitted: bool


class DataSettings(FrozenModel):
    providers: tuple[str, ...]
    max_age_seconds: int = Field(gt=0)
    quality_threshold: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))


class StrategySettings(FrozenModel):
    enabled: tuple[str, ...]
    rebalance_interval: str
    signal_threshold: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    cost_multiplier: Decimal = Field(ge=Decimal("2"))


class PortfolioSettings(FrozenModel):
    target_annualized_vol: Decimal = Field(gt=Decimal("0"))
    covariance_method: str
    long_only: bool


class RiskSettings(FrozenModel):
    enabled: bool
    fail_closed: bool
    max_gross_exposure: Decimal = Field(ge=Decimal("0"))
    max_net_exposure: Decimal = Field(ge=Decimal("0"))


class ExecutionSettings(FrozenModel):
    adapter: str
    external_orders_enabled: bool
    withdrawals_enabled: bool
    transfers_enabled: bool


class ControlSettings(FrozenModel):
    read_only_default: bool
    require_mfa_in_live: bool
    require_step_up_for: tuple[str, ...]
    allowed_origins: tuple[str, ...]


class DashboardSettings(FrozenModel):
    environment_banner: bool
    enable_pwa: bool
    cache_sensitive_responses: bool


class NotificationSettings(FrozenModel):
    enabled_channels: tuple[str, ...]
    sev1_requires_acknowledgement: bool


class ObservabilitySettings(FrozenModel):
    json_logging: bool
    metrics_enabled: bool


class DisasterRecoverySettings(FrozenModel):
    critical_trading_events_rpo_seconds: int = Field(ge=0)
    audit_events_rpo_seconds: int = Field(ge=0)
    establish_safe_known_state_rto_minutes: int = Field(gt=0)
    full_trading_resume: str
    backup_restore_drill_frequency_days: int = Field(gt=0)
    auto_resume_after_restore: bool
    recovery_mode: str


class LeadershipSettings(FrozenModel):
    single_active_required: bool
    fencing_token_required: bool
    lease_ttl_seconds: int = Field(gt=0)
    fail_on_unknown_authority: bool


class CredentialSecuritySettings(FrozenModel):
    real_credentials_allowed: bool
    withdrawals_permission_allowed: bool
    transfers_permission_allowed: bool
    revoke_on_compromise: bool


class VenueHealthSettings(FrozenModel):
    default_state: str
    unknown_state_action: str
    block_risk_on_withdrawal_suspension: bool


class QuoteAssetRiskSettings(FrozenModel):
    minimum_confirming_sources: int = Field(ge=2)
    watch_deviation_bps: int = Field(gt=0)
    close_only_deviation_bps: int = Field(gt=0)
    halt_deviation_bps: int = Field(gt=0)
    insufficient_sources_action: str

    @model_validator(mode="after")
    def validate_threshold_order(self) -> QuoteAssetRiskSettings:
        if not (self.watch_deviation_bps < self.close_only_deviation_bps < self.halt_deviation_bps):
            raise ValueError("quote-asset thresholds must increase from watch to halt")
        return self


class IncidentResponseSettings(FrozenModel):
    sev1_ack_minutes: int = Field(gt=0)
    sev2_ack_minutes: int = Field(gt=0)
    unresolved_sev1_action: str
    live_restart_requires_two_person_approval: bool
    post_incident_maximum_mode: EnvironmentMode
    primary_and_backup_notification_channels_required: bool


class MarketProfile(FrozenModel):
    profile_id: str
    asset_class: str
    enabled: bool
    session_model: str
    leverage_allowed: bool
    short_allowed: bool
    transfers_allowed: bool
    extended_hours_allowed: bool
    corporate_action_checks_required: bool
    venue_and_quote_asset_limits_required: bool


class Settings(FrozenModel):
    schema_version: str
    system: SystemSettings
    data: DataSettings
    strategy: StrategySettings
    portfolio: PortfolioSettings
    risk: RiskSettings
    execution: ExecutionSettings
    control: ControlSettings
    dashboard: DashboardSettings
    notifications: NotificationSettings
    observability: ObservabilitySettings
    disaster_recovery: DisasterRecoverySettings
    leadership: LeadershipSettings
    credential_security: CredentialSecuritySettings
    venue_health: VenueHealthSettings
    quote_asset_risk: QuoteAssetRiskSettings
    incident_response: IncidentResponseSettings
    market: MarketProfile

    @model_validator(mode="after")
    def enforce_bootstrap_safety(self) -> Settings:
        prohibited_modes = {EnvironmentMode.CANARY, EnvironmentMode.LIVE}
        if self.system.mode in prohibited_modes:
            raise ValueError("Milestone 0 cannot start canary or live mode")
        if not self.system.startup_permitted:
            raise ValueError("configuration explicitly prohibits startup")
        if self.system.live_enabled:
            raise ValueError("live must remain disabled in Milestone 0")
        if self.execution.adapter != "mock" or self.execution.external_orders_enabled:
            raise ValueError("only the mock execution adapter is permitted")
        if self.execution.withdrawals_enabled or self.execution.transfers_enabled:
            raise ValueError("withdrawals and transfers must remain disabled")
        if self.credential_security.real_credentials_allowed:
            raise ValueError("real credentials are forbidden in Milestone 0")
        if not self.risk.fail_closed:
            raise ValueError("risk configuration must fail closed")
        if self.disaster_recovery.auto_resume_after_restore:
            raise ValueError("automatic trading resume after restore is forbidden")
        if self.disaster_recovery.recovery_mode.lower() != "halt":
            raise ValueError("restore must default to halt")
        if not (
            self.leadership.single_active_required
            and self.leadership.fencing_token_required
            and self.leadership.fail_on_unknown_authority
        ):
            raise ValueError("single-active fenced leadership is required")
        if not self.incident_response.live_restart_requires_two_person_approval:
            raise ValueError("live restart must require two-person approval")
        return self
