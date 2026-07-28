import { describe, expect, it } from "vitest";

import { mockSystemStatus, statusLabel } from "../lib/mock-status";

describe("Milestone 0 mock status", () => {
  it("cannot represent external or live trading as enabled", () => {
    expect(mockSystemStatus.externalTradingEnabled).toBe(false);
    expect(mockSystemStatus.liveEnabled).toBe(false);
    expect(statusLabel(mockSystemStatus)).toBe("RESEARCH · HALT · NOT TRADABLE");
  });
});
