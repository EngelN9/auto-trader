export type MockSystemStatus = Readonly<{
  environment: "RESEARCH";
  riskState: "HALT";
  marketData: "MOCK";
  execution: "MOCK";
  externalTradingEnabled: false;
  liveEnabled: false;
}>;

export const mockSystemStatus: MockSystemStatus = Object.freeze({
  environment: "RESEARCH",
  riskState: "HALT",
  marketData: "MOCK",
  execution: "MOCK",
  externalTradingEnabled: false,
  liveEnabled: false,
});

export function statusLabel(status: MockSystemStatus): string {
  return `${status.environment} · ${status.riskState} · NOT TRADABLE`;
}
