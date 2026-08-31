import { useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8007";

type Investigation = {
  transaction?: any;
  account?: any;
  historical_baseline?: any;
  security_context?: any;
  detection?: any;
};

function App() {
  const [transactionId, setTransactionId] = useState("TX-FRAUD-001");
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const investigate = async () => {
    setLoading(true);
    setMessage("");

    try {
      const res = await fetch(`${API}/investigate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transaction_id: transactionId }),
      });

      const data = await res.json();

      if (!data.found) {
        setInvestigation(null);
        setMessage(data.message || "Transaction not found.");
      } else {
        setInvestigation(data);
        setResponse(null);
      }
    } catch {
      setMessage("Unable to connect to HORUS backend.");
    } finally {
      setLoading(false);
    }
  };

  const executeContainment = async () => {
    setLoading(true);
    setMessage("");

    try {
      const res = await fetch(`${API}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transaction_id: transactionId }),
      });

      const data = await res.json();
      setResponse(data);
      setMessage(
        data.success
          ? "Containment workflow completed successfully."
          : "Containment workflow failed."
      );
    } catch {
      setMessage("Unable to execute containment.");
    } finally {
      setLoading(false);
    }
  };

  const detection = investigation?.detection;
  const riskScore = response?.risk_score ?? detection?.raw_score ?? 0;
  const riskLevel = response?.risk_level ?? (riskScore >= 80 ? "CRITICAL" : "HIGH");

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <div className="logo">HORUS</div>
          <div className="subtitle">Financial Security Operations Platform</div>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          SYSTEM OPERATIONAL
        </div>
      </header>

      <main>
        <section className="search-panel">
          <div>
            <h1>Security Operations Console</h1>
            <p>Investigate suspicious financial activity and manage containment.</p>
          </div>

          <div className="search-box">
            <input
              value={transactionId}
              onChange={(e) => setTransactionId(e.target.value)}
              placeholder="Transaction ID"
            />
            <button onClick={investigate} disabled={loading}>
              {loading ? "PROCESSING..." : "INVESTIGATE"}
            </button>
          </div>
        </section>

        {message && <div className="message">{message}</div>}

        {!investigation && (
          <div className="empty-state">
            <div className="empty-icon">◉</div>
            <h2>No investigation selected</h2>
            <p>Enter a transaction ID to begin a security investigation.</p>
          </div>
        )}

        {investigation && (
          <>
            <section className="overview-grid">
              <div className="card">
                <span className="label">TRANSACTION</span>
                <strong>{investigation.transaction?.transaction_id}</strong>
                <small>{investigation.transaction?.merchant}</small>
              </div>

              <div className="card">
                <span className="label">ACCOUNT</span>
                <strong>{investigation.account?.account_id}</strong>
                <small>{investigation.account?.customer_name}</small>
              </div>

              <div className="card">
                <span className="label">AMOUNT</span>
                <strong>
                  ₦{Number(investigation.transaction?.amount || 0).toLocaleString()}
                </strong>
                <small>{investigation.transaction?.currency}</small>
              </div>

              <div className={`card risk ${riskLevel.toLowerCase()}`}>
                <span className="label">RISK LEVEL</span>
                <strong>{riskLevel}</strong>
                <small>Score: {riskScore}/100</small>
              </div>
            </section>

            <section className="content-grid">
              <div className="panel">
                <div className="panel-header">
                  <h2>Detected Anomalies</h2>
                  <span>{detection?.triggered_rules?.length || 0} signals</span>
                </div>

                <div className="signals">
                  {detection?.triggered_rules?.map((rule: any) => (
                    <div className="signal" key={rule.rule}>
                      <div className="signal-title">
                        <span className="signal-dot" />
                        {rule.rule}
                        <b>+{rule.score}</b>
                      </div>
                      <p>{rule.reason}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h2>Account Intelligence</h2>
                </div>

                <div className="intel-list">
                  <div>
                    <span>Registered Location</span>
                    <strong>
                      {investigation.account?.city},{" "}
                      {investigation.account?.country}
                    </strong>
                  </div>

                  <div>
                    <span>Transaction Location</span>
                    <strong>{investigation.transaction?.location}</strong>
                  </div>

                  <div>
                    <span>Device</span>
                    <strong>{investigation.transaction?.device_id}</strong>
                  </div>

                  <div>
                    <span>Device Trust</span>
                    <strong>
                      {investigation.historical_baseline?.untrusted_devices?.includes(
                        investigation.transaction?.device_id
                      )
                        ? "UNTRUSTED"
                        : "TRUSTED"}
                    </strong>
                  </div>

                  <div>
                    <span>Historical Average</span>
                    <strong>
                      ₦
                      {Number(
                        investigation.historical_baseline?.average_amount || 0
                      ).toLocaleString()}
                    </strong>
                  </div>

                  <div>
                    <span>Account Status</span>
                    <strong>{investigation.account?.status}</strong>
                  </div>
                </div>
              </div>
            </section>

            <section className="panel">
              <div className="panel-header">
                <h2>Containment</h2>
                <span>Explicit authorization required</span>
              </div>

              {!response ? (
                <div className="containment">
                  <div>
                    <h3>Recommended response</h3>
                    <p>
                      HORUS has identified a {riskLevel.toLowerCase()}-risk
                      transaction. Execute the deterministic containment
                      workflow to apply the response policy.
                    </p>
                  </div>

                  <button
                    className="danger-button"
                    onClick={executeContainment}
                    disabled={loading}
                  >
                    EXECUTE CONTAINMENT
                  </button>
                </div>
              ) : (
                <div className="results">
                  <div className="execution-header">
                    <h3>
                      {response.success
                        ? "Containment Completed"
                        : "Containment Failed"}
                    </h3>
                    <span>{response.incident_id}</span>
                  </div>

                  {response.execution?.results?.map(
                    (result: any, index: number) => (
                      <div className="action-result" key={index}>
                        <span className="check">
                          {result.success !== false ? "✓" : "×"}
                        </span>

                        <div>
                          <strong>
                            {result.action || "FLAG_TRANSACTIONS"}
                          </strong>

                          <small>
                            {result.account_id ||
                              result.device_id ||
                              result.transaction_id ||
                              result.incident?.incident_id ||
                              "Multiple transactions"}
                          </small>
                        </div>

                        <span className="success-text">
                          {result.success !== false ? "SUCCESS" : "FAILED"}
                        </span>
                      </div>
                    )
                  )}
                </div>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;