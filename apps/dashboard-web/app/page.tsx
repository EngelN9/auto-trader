import { mockSystemStatus, statusLabel } from "../lib/mock-status";

const services = [
  { name: "Control API", state: "Mock healthy", detail: "Read-only health surface" },
  { name: "Trading runtime", state: "Halted", detail: "External orders disabled" },
  { name: "Mock broker", state: "Isolated", detail: "No order submission route" },
  { name: "PostgreSQL", state: "Development", detail: "No production ledger" },
] as const;

export default function DashboardPage() {
  return (
    <main>
      <header className="topbar">
        <div>
          <p className="eyebrow">AUTO TRADER / CONTROL PLANE</p>
          <h1>Operations overview</h1>
        </div>
        <div className="environment-badge">{statusLabel(mockSystemStatus)}</div>
      </header>

      <section className="warning" aria-label="Milestone warning">
        <strong>Milestone 0 skeleton</strong>
        <span>
          All values are deterministic mock data. No exchange, broker, account, or live credential
          is connected.
        </span>
      </section>

      <section className="metrics" aria-label="Mock portfolio metrics">
        <article>
          <p>Net asset value</p>
          <strong>—</strong>
          <span>No account connected</span>
        </article>
        <article>
          <p>Gross exposure</p>
          <strong>0.00%</strong>
          <span>Risk budget locked</span>
        </article>
        <article>
          <p>Open orders</p>
          <strong>0</strong>
          <span>Submission unavailable</span>
        </article>
        <article>
          <p>Risk state</p>
          <strong>{mockSystemStatus.riskState}</strong>
          <span>Fail-closed default</span>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">SERVICE BOUNDARIES</p>
            <h2>Development topology</h2>
          </div>
          <span className="mock-chip">MOCK DATA</span>
        </div>
        <div className="service-list">
          {services.map((service) => (
            <article key={service.name}>
              <span className="status-dot" aria-hidden="true" />
              <div>
                <strong>{service.name}</strong>
                <p>{service.detail}</p>
              </div>
              <span>{service.state}</span>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
