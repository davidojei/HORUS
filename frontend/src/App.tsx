import { useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Clock3,
  CreditCard,
  Database,
  FileWarning,
  Lock,
  Menu,
  Search,
  Shield,
  ShieldAlert,
  Smartphone,
  Terminal,
  UserRound,
  X,
  Zap,
} from "lucide-react";
import "./App.css";

const API = "http://127.0.0.1:8007";

type Investigation = {
  found: boolean;
  transaction?: {
    transaction_id: string;
    account_id: string;
    amount: number;
    currency: string;
    merchant: string;
    location: string;
    device_id: string;
    timestamp: string;
    status: string;
    fraud_flag?: boolean;
    incident_id?: string;
  };
  account?: {
    account_id: string;
    customer_name: string;
    country: string;
    city: string;
    account_type: string;
    risk_score: number;
    status: string;
  };
  historical_baseline?: {
    transaction_count: number;
    average_amount: number;
    maximum_amount: number;
    historical_locations: string[];
    trusted_devices: string[];
    untrusted_devices: string[];
  };
  security_context?: {
    known_device_count: number;
    untrusted_device_count: number;
    login_event_count: number;
  };
  detection?: {
    triggered_rules?: {
      rule: string;
      triggered: boolean;
      score: number;
      reason: string;
    }[];
    raw_score: number;
  };
};

type AuditEvent = {
  timestamp: string;
  incident_id: string;
  transaction_id: string;
  action: string;
  target: string;
  status: string;
};

function App() {
  const [transactionId, setTransactionId] = useState("TX-FRAUD-001");
  const [investigation, setInvestigation] = useState<Investigation | null>(
    null,
  );
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState("");

  const investigate = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API}/investigate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transaction_id: transactionId }),
      });

      if (!response.ok) throw new Error("Investigation request failed.");

      const data = await response.json();
      setInvestigation(data);

      if (data.transaction?.incident_id) {
        await loadAudit(data.transaction.incident_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to investigate.");
    } finally {
      setLoading(false);
    }
  };

  const executeContainment = async () => {
    setExecuting(true);
    setError("");

    try {
      const response = await fetch(`${API}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transaction_id: transactionId }),
      });

      if (!response.ok) throw new Error("Containment request failed.");

      const data = await response.json();

      if (data.incident_id) {
        await loadAudit(data.incident_id);
      }

      await investigate();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to execute containment.",
      );
    } finally {
      setExecuting(false);
    }
  };

  const loadAudit = async (incidentId: string) => {
    try {
      const response = await fetch(`${API}/incidents/${incidentId}/audit`);
      if (!response.ok) return;

      const data = await response.json();
      setAudit(data.events ?? []);
    } catch {
      // Audit is supplementary UI data.
    }
  };

  const tx = investigation?.transaction;
  const account = investigation?.account;
  const baseline = investigation?.historical_baseline;
  const detection = investigation?.detection;

  const riskScore = detection?.raw_score ?? 0;
  const critical = riskScore >= 80;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Shield size={22} />
          </div>
          <div>
            <div className="brand-name">HORUS</div>
            <div className="brand-subtitle">SECURITY OPERATIONS</div>
          </div>
        </div>

        <nav className="nav">
          <button className="nav-item active">
            <Activity size={18} />
            Overview
          </button>

          <button className="nav-item">
            <ShieldAlert size={18} />
            Incidents
            <span className="nav-count">{audit.length > 0 ? "1" : "0"}</span>
          </button>

          <button className="nav-item">
            <CreditCard size={18} />
            Transactions
          </button>

          <button className="nav-item">
            <Smartphone size={18} />
            Devices
          </button>

          <button className="nav-item">
            <Database size={18} />
            Audit Log
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="status-dot" />
            <div>
              <strong>System operational</strong>
              <span>API connected</span>
            </div>
          </div>

          <div className="version">
            HORUS v1.0.0
            <span>ENTERPRISE SECURITY</span>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="mobile-menu">
            <Menu size={20} />
          </div>

          <div>
            <div className="eyebrow">FINANCIAL SECURITY</div>
            <h1>Operations Console</h1>
          </div>

          <div className="topbar-right">
            <div className="live-indicator">
              <span />
              LIVE
            </div>
            <div className="operator">
              <div className="operator-avatar">
                <UserRound size={17} />
              </div>
              <div>
                <strong>Security Operator</strong>
                <small>Authorized</small>
              </div>
            </div>
          </div>
        </header>

        <section className="content">
          <div className="command-bar">
            <div className="search-box">
              <Search size={18} />
              <input
                value={transactionId}
                onChange={(e) => setTransactionId(e.target.value)}
                placeholder="Enter transaction ID..."
                onKeyDown={(e) => {
                  if (e.key === "Enter") investigate();
                }}
              />
            </div>

            <button
              className="investigate-btn"
              onClick={investigate}
              disabled={loading || !transactionId}
            >
              {loading ? "Investigating..." : "Investigate Transaction"}
              {!loading && <ChevronRight size={18} />}
            </button>
          </div>

          {error && (
            <div className="error-banner">
              <AlertTriangle size={18} />
              {error}
              <button onClick={() => setError("")}>
                <X size={16} />
              </button>
            </div>
          )}

          {!investigation && !loading && (
            <div className="empty-state">
              <div className="empty-icon">
                <Terminal size={28} />
              </div>
              <h2>Ready for investigation</h2>
              <p>
                Enter a transaction ID above to analyze financial activity,
                detect anomalies, and review containment options.
              </p>
              <button onClick={investigate}>
                Investigate TX-FRAUD-001
              </button>
            </div>
          )}

          {loading && (
            <div className="empty-state">
              <div className="loading-ring" />
              <h2>Analyzing transaction</h2>
              <p>
                HORUS is gathering enterprise evidence and evaluating
                deterministic fraud signals.
              </p>
            </div>
          )}

          {investigation && tx && account && (
            <>
              <div className="incident-header">
                <div>
                  <div className="eyebrow">ACTIVE INVESTIGATION</div>
                  <h2>
                    {tx.incident_id || "NO INCIDENT"}{" "}
                    <span className="open-badge">OPEN</span>
                  </h2>
                </div>

                <div className="incident-time">
                  <Clock3 size={15} />
                  {new Date(tx.timestamp).toLocaleString()}
                </div>
              </div>

              <div className="dashboard-grid">
                <section className="card risk-card">
                  <div className="card-header">
                    <span>RISK ASSESSMENT</span>
                    <ShieldAlert size={18} />
                  </div>

                  <div className={`risk-score ${critical ? "critical" : ""}`}>
                    <strong>{riskScore}</strong>
                    <span>/ 100</span>
                  </div>

                  <div className="risk-level">
                    <span className="risk-dot" />
                    {critical ? "CRITICAL" : "ELEVATED"}
                  </div>

                  <div className="risk-bar">
                    <div style={{ width: `${Math.min(riskScore, 100)}%` }} />
                  </div>

                  <p className="muted">
                    Deterministic risk engine assessment
                  </p>
                </section>

                <section className="card transaction-card">
                  <div className="card-header">
                    <span>TRANSACTION</span>
                    <CreditCard size={18} />
                  </div>

                  <div className="transaction-amount">
                    ₦{tx.amount.toLocaleString()}
                  </div>

                  <div className="merchant">{tx.merchant}</div>

                  <div className="detail-grid">
                    <Detail label="Transaction ID" value={tx.transaction_id} />
                    <Detail label="Account" value={tx.account_id} />
                    <Detail label="Location" value={tx.location} />
                    <Detail label="Device" value={tx.device_id} />
                  </div>
                </section>

                <section className="card account-card">
                  <div className="card-header">
                    <span>ACCOUNT</span>
                    <UserRound size={18} />
                  </div>

                  <div className="account-name">{account.customer_name}</div>
                  <div className="account-type">
                    {account.account_type} ACCOUNT
                  </div>

                  <div className="account-status">
                    <span className="status-dot" />
                    {account.status}
                  </div>

                  <div className="detail-grid">
                    <Detail label="Account ID" value={account.account_id} />
                    <Detail label="Registered City" value={account.city} />
                    <Detail label="Country" value={account.country} />
                    <Detail
                      label="Account Risk"
                      value={`${account.risk_score}/100`}
                    />
                  </div>
                </section>
              </div>

              <div className="section-title">
                <div>
                  <div className="eyebrow">DETECTION ENGINE</div>
                  <h2>Why HORUS flagged this activity</h2>
                </div>
                <span className="deterministic">
                  <Zap size={14} /> DETERMINISTIC
                </span>
              </div>

              <section className="signals-grid">
                {detection?.triggered_rules?.map((rule) => (
                  <div className="signal-card" key={rule.rule}>
                    <div className="signal-top">
                      <div className="signal-icon">
                        <AlertTriangle size={17} />
                      </div>
                      <span>+{rule.score}</span>
                    </div>
                    <h3>{formatRule(rule.rule)}</h3>
                    <p>{rule.reason}</p>
                  </div>
                ))}
              </section>

              <div className="lower-grid">
                <section className="card containment-card">
                  <div className="card-header">
                    <div>
                      <span>RESPONSE</span>
                      <h2>Containment</h2>
                    </div>
                    <Lock size={18} />
                  </div>

                  <div className="containment-warning">
                    <AlertTriangle size={18} />
                    <div>
                      <strong>Explicit authorization required</strong>
                      <p>
                        Executing containment modifies enterprise state.
                        Review the evidence before proceeding.
                      </p>
                    </div>
                  </div>

                  <button
                    className="contain-btn"
                    onClick={executeContainment}
                    disabled={executing}
                  >
                    {executing
                      ? "Executing containment..."
                      : "Execute Recommended Containment"}
                  </button>
                </section>

                <section className="card baseline-card">
                  <div className="card-header">
                    <div>
                      <span>BEHAVIORAL BASELINE</span>
                      <h2>Account history</h2>
                    </div>
                    <Activity size={18} />
                  </div>

                  <div className="baseline-stats">
                    <Metric
                      label="Transactions"
                      value={baseline?.transaction_count ?? 0}
                    />
                    <Metric
                      label="Average"
                      value={`₦${Math.round(
                        baseline?.average_amount ?? 0,
                      ).toLocaleString()}`}
                    />
                    <Metric
                      label="Max"
                      value={`₦${Math.round(
                        baseline?.maximum_amount ?? 0,
                      ).toLocaleString()}`}
                    />
                  </div>

                  <div className="device-summary">
                    <div>
                      <span className="green-dot" />
                      Trusted devices
                      <strong>{baseline?.trusted_devices.length ?? 0}</strong>
                    </div>
                    <div>
                      <span className="red-dot" />
                      Untrusted devices
                      <strong>{baseline?.untrusted_devices.length ?? 0}</strong>
                    </div>
                  </div>
                </section>
              </div>

              <section className="card audit-card">
                <div className="card-header">
                  <div>
                    <span>AUDIT TRAIL</span>
                    <h2>Incident activity</h2>
                  </div>
                  <Database size={18} />
                </div>

                {audit.length === 0 ? (
                  <div className="audit-empty">
                    No containment actions recorded for this incident.
                  </div>
                ) : (
                  <div className="audit-list">
                    {audit.slice(-8).map((event, index) => (
                      <div className="audit-row" key={`${event.timestamp}-${index}`}>
                        <div className="audit-icon">
                          <CheckCircle2 size={16} />
                        </div>

                        <div className="audit-main">
                          <strong>{formatRule(event.action)}</strong>
                          <span>{event.target}</span>
                        </div>

                        <div className="audit-status">{event.status}</div>

                        <time>
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </time>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="detail">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function formatRule(value: string) {
  return value
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export default App;