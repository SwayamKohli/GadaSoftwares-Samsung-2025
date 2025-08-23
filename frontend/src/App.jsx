import { useState, useEffect } from 'react';
import './App.css';

function App() {
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

  // Real-time flow data (separate for UE-1 and UE-2)
  const [logs1, setLogs1] = useState([]);
  const [logs2, setLogs2] = useState([]);

  // Simulate live data
  useEffect(() => {
    const apps = [
      // Real-Time
      { name: "WhatsApp Call", isRealTime: true },
      { name: "Zoom Meeting", isRealTime: true },
      { name: "Fortnite", isRealTime: true },
      { name: "Discord Voice", isRealTime: true },
      { name: "FaceTime", isRealTime: true },

      // Non-Real-Time
      { name: "Google Browsing", isRealTime: false },
      { name: "YouTube Video", isRealTime: false },
      { name: "Instagram Reels", isRealTime: false },
      { name: "Gmail Sync", isRealTime: false },
      { name: "Spotify Music", isRealTime: false },
      { name: "Microsoft Docs", isRealTime: false }
    ];

    const protocols = ["TCP", "UDP"];
    const generateLog = (id, app) => {
      const protocol = protocols[Math.floor(Math.random() * protocols.length)];
      const size = Math.floor(Math.random() * 1500) + 64;
      const duration = (Math.random() * 10).toFixed(2);
      return `[UE-${id}] ${new Date().toLocaleTimeString()} | App: ${app.name} | Proto: ${protocol} | Size: ${size}B | Dur: ${duration}s`;
    };

    const interval = setInterval(() => {
      // Randomly update UE-1
      if (Math.random() > 0.7) {
        const app1 = apps[Math.floor(Math.random() * apps.length)];
        setUe1({
          app: app1.name,
          type: app1.isRealTime ? "REAL-TIME" : "NON-REAL-TIME",
          confidence: `${Math.floor(Math.random() * 15) + 85}%`,
          qos: app1.isRealTime
            ? "Low Latency, Low Jitter, High Priority"
            : "Medium Latency OK, Low Priority"
        });
        setLogs1(prev => [generateLog(1, app1), ...prev.slice(0, 49)]);
      }

      // Randomly update UE-2
      if (Math.random() > 0.7) {
        const app2 = apps[Math.floor(Math.random() * apps.length)];
        setUe2({
          app: app2.name,
          type: app2.isRealTime ? "REAL-TIME" : "NON-REAL-TIME",
          confidence: `${Math.floor(Math.random() * 15) + 85}%`,
          qos: app2.isRealTime
            ? "Low Latency, Low Jitter, High Priority"
            : "Medium Latency OK, Low Priority"
        });
        setLogs2(prev => [generateLog(2, app2), ...prev.slice(0, 49)]);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>GadaSoftware</h1>
        <p>Network Intelligence Dashboard | Real-Time vs Non-Real-Time Detection</p>
      </header>

      <main className="dashboard">
        {/* User Cards */}
        <div className="user-section">
          <div className={`ue-card ${ue1.type === 'REAL-TIME' ? 'realtime' : 'non-realtime'}`}>
            <h2>UE-1: Smartphone</h2>
            <p><strong>Current App:</strong> {ue1.app}</p>
          </div>

          <div className={`ue-card ${ue2.type === 'REAL-TIME' ? 'realtime' : 'non-realtime'}`}>
            <h2>UE-2: Tablet</h2>
            <p><strong>Current App:</strong> {ue2.app}</p>
          </div>
        </div>

        {/* Log Streams */}
        <div className="logs-section">
          <div className="log-container">
            <h3>📡 UE-1 Traffic Flow (Latest 50 Entries)</h3>
            <div className="log-frame">
              {logs1.length === 0 ? (
                <div className="log-entry">Waiting for traffic...</div>
              ) : (
                logs1.map((log, i) => (
                  <div key={i} className="log-entry">{log}</div>
                ))
              )}
            </div>
          </div>

          <div className="log-container">
            <h3>📡 UE-2 Traffic Flow (Latest 50 Entries)</h3>
            <div className="log-frame">
              {logs2.length === 0 ? (
                <div className="log-entry">Waiting for traffic...</div>
              ) : (
                logs2.map((log, i) => (
                  <div key={i} className="log-entry">{log}</div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Status */}
        <div className="status-section">
          <div className="status-box">
            <h3>🚦 UE-1 Status</h3>
            <p><strong>Type:</strong> <span className={`badge ${ue1.type}`}>{ue1.type}</span></p>
            <p><strong>Confidence:</strong> <span className="highlight">{ue1.confidence}</span></p>
            <p><strong>QoS Recommendation:</strong></p>
            <p className="qos">{ue1.qos}</p>
          </div>

          <div className="status-box">
            <h3>🚦 UE-2 Status</h3>
            <p><strong>Type:</strong> <span className={`badge ${ue2.type}`}>{ue2.type}</span></p>
            <p><strong>Confidence:</strong> <span className="highlight">{ue2.confidence}</span></p>
            <p><strong>QoS Recommendation:</strong></p>
            <p className="qos">{ue2.qos}</p>
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>Auto-refresh enabled | GadaSoftware Network AI Engine | Simulating Multi-UE Environment</p>
      </footer>
    </div>
  );
}

export default App;