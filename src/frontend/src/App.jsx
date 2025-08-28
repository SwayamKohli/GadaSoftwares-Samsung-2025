import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [page, setPage] = useState('welcome');

  const [ue1, setUe1] = useState({
    app: "Idle",
    type: "Unknown",
    confidence: "0%",
    qos: "No recommendation"
  });
  const [ue2, setUe2] = useState({
    app: "Idle",
    type: "Unknown",
    confidence: "0%",
    qos: "No recommendation"
  });
  const [logs1, setLogs1] = useState([]);
  const [logs2, setLogs2] = useState([]);

  const [testData, setTestData] = useState([]);
  const [index1, setIndex1] = useState(0);
  const [index2, setIndex2] = useState(1); // Start UE-2 slightly offset

  // Capitalize first letter of each word
  const toTitleCase = (str) => {
    return str.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
  };

  // Format QoS policy as clean list
  const formatQoS = (qosObj) => {
    if (!qosObj) return "No QoS policy";
    return Object.entries(qosObj)
      .map(([key, value]) => `${toTitleCase(key)}: ${toTitleCase(value)}`)
      .join(' | ');
  };

  // Fetch real test data from website_testing.csv via backend
  useEffect(() => {
    const loadTestData = async () => {
      try {
        const response = await fetch('http://localhost:8000/test-website?limit=100');
        if (!response.ok) throw new Error('Failed to load test data');
        const result = await response.json();
        if (result.predictions && result.predictions.length > 0) {
          setTestData(result.predictions);
          console.log("✅ Loaded", result.predictions.length, "test samples from website_testing.csv");
        } else {
          console.warn("⚠️ No predictions returned from /test-website");
        }
      } catch (err) {
        console.error("❌ Failed to load test data:", err);
      }
    };

    if (page === 'dashboard') {
      loadTestData();
    }
  }, [page]);

  // Simulate live data with real API
  useEffect(() => {
    if (page !== 'dashboard' || testData.length === 0) return;

    const interval = setInterval(() => {
      // Pick next sample for UE-1
      const sample1 = testData[index1];
      // Pick different sample for UE-2 (avoid sync)
      const sample2 = testData[index2];

      // Update UE-1
      if (sample1) {
        let qosPolicy = "No QoS policy";
        fetch(`http://localhost:8000/qos?class_label=${encodeURIComponent(sample1.predicted)}`)
          .then(r => r.json())
          .then(qosData => {
            if (qosData && qosData.qos) {
              qosPolicy = formatQoS(qosData.qos);
            }
          })
          .catch(err => {
            console.warn("QoS fetch failed for UE-1:", err);
            qosPolicy = "QoS: Default Policy";
          })
          .finally(() => {
            const confidence = sample1.confidence
              ? `${(sample1.confidence * 100).toFixed(1)}%`
              : 'N/A';
            const confidenceForLog = sample1.confidence ? sample1.confidence.toFixed(2) : 'N/A';
            const appDisplayName = sample1.predicted || "Unknown";

            const now = new Date();
            const timeStr = now.toLocaleTimeString('en-US', {
              hour: 'numeric',
              minute: '2-digit',
              second: '2-digit',
              hour12: true
            });

            setUe1({
              app: appDisplayName,
              type: appDisplayName,
              confidence,
              qos: qosPolicy
            });
            setLogs1(prev => [
              `[UE-1] ${timeStr} | App: ${appDisplayName} | Pred: ${appDisplayName} (${confidenceForLog})`,
              ...prev.slice(0, 49)
            ]);
          });
      }

      // Update UE-2
      if (sample2) {
        let qosPolicy = "No QoS policy";
        fetch(`http://localhost:8000/qos?class_label=${encodeURIComponent(sample2.predicted)}`)
          .then(r => r.json())
          .then(qosData => {
            if (qosData && qosData.qos) {
              qosPolicy = formatQoS(qosData.qos);
            }
          })
          .catch(err => {
            console.warn("QoS fetch failed for UE-2:", err);
            qosPolicy = "QoS: Default Policy";
          })
          .finally(() => {
            const confidence = sample2.confidence
              ? `${(sample2.confidence * 100).toFixed(1)}%`
              : 'N/A';
            const confidenceForLog = sample2.confidence ? sample2.confidence.toFixed(2) : 'N/A';
            const appDisplayName = sample2.predicted || "Unknown";

            const now = new Date();
            const timeStr = now.toLocaleTimeString('en-US', {
              hour: 'numeric',
              minute: '2-digit',
              second: '2-digit',
              hour12: true
            });

            setUe2({
              app: appDisplayName,
              type: appDisplayName,
              confidence,
              qos: qosPolicy
            });
            setLogs2(prev => [
              `[UE-2] ${timeStr} | App: ${appDisplayName} | Pred: ${appDisplayName} (${confidenceForLog})`,
              ...prev.slice(0, 49)
            ]);
          });
      }

      // Move to next indices
      setIndex1((prev) => (prev + 1) % testData.length);
      setIndex2((prev) => (prev + 2) % testData.length); // Faster offset

    }, 2000); // Update every 2 seconds

    return () => clearInterval(interval);
  }, [page, testData, index1, index2]);

  const saveLogsToCSV = (ueId) => {
    const logs = ueId === 1 ? logs1 : logs2;
    const filename = `UE-${ueId}_Traffic_Logs.csv`;
    const header = "Timestamp,App,Prediction,Confidence\n";
    const rows = logs.map(log => {
      const match = log.match(/\[UE-\d+\] (.*?) \| App: (.*?) \| Pred: (.*?) \((.*?)\)/);
      if (match) {
        return `"${match[1].trim()}","${match[2].trim()}","${match[3].trim()}","${match[4].trim()}"`;
      }
      return "";
    }).join("\n");

    const csv = header + rows;
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const renderPage = () => {
    switch (page) {
      case 'welcome':
        return (
          <div className="page welcome">
            <div className="background-effects"></div>
            <header className="header">
              <h1>CATO</h1>
              <p>Classification of Application Traffic Online</p>
            </header>
            <main className="content welcome-content">
              <h2>Welcome to CATO</h2>
              <p>Using real-world test data </p>
              <button className="btn-primary" onClick={() => setPage('dashboard')}>
                Start Monitoring
              </button>
            </main>
            <footer className="footer">
              <p>Team GadaSoftwares | Samsung Hackathon 2025</p>
            </footer>
          </div>
        );

      case 'dashboard':
        return (
          <div className="page dashboard">
            <header className="header">
              <h1>CATO</h1>
              <p>Live Multi-Class Traffic Monitoring</p>
            </header>
            <nav className="nav">
              <button onClick={() => setPage('welcome')} className="nav-btn">Home</button>
              <button onClick={() => setPage('logs')} className="nav-btn">View Logs</button>
            </nav>
            <main className="content dashboard-content">
              <div className="ue-column">
                <div className="ue-card">
                  <h2>UE-1: Smartphone</h2>
                  <p><strong>Current App:</strong> {ue1.app}</p>
                </div>
                <div className="status-box">
                  <h3>UE-1 Status</h3>
                  <p><strong>Type:</strong> <span className="badge">{ue1.type}</span></p>
                  <p><strong>Confidence:</strong> <span className="highlight">{ue1.confidence}</span></p>
                  <p><strong>QoS Recommendation:</strong></p>
                  <p className="qos">{ue1.qos}</p>
                </div>
              </div>
              <div className="ue-column">
                <div className="ue-card">
                  <h2>UE-2: Tablet</h2>
                  <p><strong>Current App:</strong> {ue2.app}</p>
                </div>
                <div className="status-box">
                  <h3>UE-2 Status</h3>
                  <p><strong>Type:</strong> <span className="badge">{ue2.type}</span></p>
                  <p><strong>Confidence:</strong> <span className="highlight">{ue2.confidence}</span></p>
                  <p><strong>QoS Recommendation:</strong></p>
                  <p className="qos">{ue2.qos}</p>
                </div>
              </div>
              <div className="logs-section">
                <div className="log-container">
                  <h3>UE-1 Traffic Flow (Latest 50)</h3>
                  <div className="log-frame">
                    {logs1.length === 0 ? (
                      <div className="log-entry">Loading...</div>
                    ) : (
                      logs1.map((log, i) => (
                        <div key={i} className="log-entry">{log}</div>
                      ))
                    )}
                  </div>
                  <button className="btn-save" onClick={() => saveLogsToCSV(1)}>
                    Save as CSV
                  </button>
                </div>
                <div className="log-container">
                  <h3>UE-2 Traffic Flow (Latest 50)</h3>
                  <div className="log-frame">
                    {logs2.length === 0 ? (
                      <div className="log-entry">Loading...</div>
                    ) : (
                      logs2.map((log, i) => (
                        <div key={i} className="log-entry">{log}</div>
                      ))
                    )}
                  </div>
                  <button className="btn-save" onClick={() => saveLogsToCSV(2)}>
                    Save as CSV
                  </button>
                </div>
              </div>
            </main>
            <footer className="footer">
              <p>Using real test data | CATO Network AI Engine</p>
            </footer>
          </div>
        );

      case 'logs':
        return (
          <div className="page logs">
            <header className="header">
              <h1>CATO</h1>
              <p>Traffic Logs</p>
            </header>
            <nav className="nav">
              <button onClick={() => setPage('dashboard')} className="nav-btn"> Back to Dashboard</button>
            </nav>
            <main className="content">
              <div className="log-container">
                <h2>UE-1 Logs</h2>
                <div className="log-frame full-height">
                  {logs1.length === 0 ? (
                    <div className="log-entry">No logs yet.</div>
                  ) : (
                    logs1.map((log, i) => (
                      <div key={i} className="log-entry">{log}</div>
                    ))
                  )}
                </div>
                <button className="btn-save" onClick={() => saveLogsToCSV(1)}>
                  Save UE-1 Logs
                </button>
              </div>
              <div className="log-container">
                <h2>UE-2 Logs</h2>
                <div className="log-frame full-height">
                  {logs2.length === 0 ? (
                    <div className="log-entry">No logs yet.</div>
                  ) : (
                    logs2.map((log, i) => (
                      <div key={i} className="log-entry">{log}</div>
                    ))
                  )}
                </div>
                <button className="btn-save" onClick={() => saveLogsToCSV(2)}>
                  Save UE-2 Logs
                </button>
              </div>
            </main>
            <footer className="footer">
              <p>All traffic logs are generated in real-time</p>
            </footer>
          </div>
        );

      default:
        return null;
    }
  };

  return <div className="app">{renderPage()}</div>;
}

export default App;