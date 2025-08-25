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

  // Simulate live data with real API
  useEffect(() => {
    const fetchPrediction = async (ueId) => {
      // Generate realistic flow features (match training data)
      const features = {
        "Source.Port": Math.floor(Math.random() * 65535),
        "Destination.Port": [80, 443, 5060, 1935, 3478, 53, 25][Math.floor(Math.random() * 7)],
        "Flow.Duration": Math.random() * 5000,
        "Total.Fwd.Packets": Math.floor(Math.random() * 50),
        "Total.Backward.Packets": Math.floor(Math.random() * 50),
        "Flow.Packets.s": Math.random() * 2000,
        "Fwd.Packet.Length.Max": Math.floor(Math.random() * 1500),
        "Flow.IAT.Max": Math.random() * 2000,
        "Bwd.Packet.Length.Max": Math.floor(Math.random() * 1500),
        "Init_Win_bytes_forward": Math.floor(Math.random() * 65535),
        "Init_Win_bytes_backward": Math.floor(Math.random() * 65535),
        "Timestamp_Formatted": Math.floor(Date.now() / 1000)
      };

      try {
        // Call backend /predict
        const response = await fetch('http://localhost:8000/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ features })
        });

        if (!response.ok) throw new Error('Prediction failed');

        const result = await response.json();

        // Fetch QoS policy
        const qosResponse = await fetch(`http://localhost:8000/qos?class_label=${result.klass}`);
        const qosData = await qosResponse.json();

        // Format confidence
        const confidence = result.confidence
          ? `${(result.confidence * 100).toFixed(1)}%`
          : 'N/A';

        // Update UE state
        const appNames = {
          'Real-Time': ['WhatsApp Call', 'Zoom Meeting', 'Fortnite', 'FaceTime', 'Discord Voice'],
          'Non-Real-Time': ['Google Browsing', 'YouTube Video', 'Instagram Reels', 'Gmail Sync', 'Spotify Music', 'Microsoft Docs']
        };
        const appList = result.klass === 'Real-Time' ? appNames['Real-Time'] : appNames['Non-Real-Time'];
        const appName = appList[Math.floor(Math.random() * appList.length)];

        if (ueId === 1) {
          setUe1({
            app: appName,
            type: result.klass.toUpperCase(),
            confidence,
            qos: Object.entries(qosData.qos)
              .map(([k, v]) => `${k}: ${v}`)
              .join(', ')
          });
          setLogs1(prev => [
            `[UE-1] ${new Date().toLocaleTimeString()} | App: ${appName} | Pred: ${result.klass} (${result.confidence?.toFixed(2)})`,
            ...prev.slice(0, 49)
          ]);
        } else {
          setUe2({
            app: appName,
            type: result.klass.toUpperCase(),
            confidence,
            qos: Object.entries(qosData.qos)
              .map(([k, v]) => `${k}: ${v}`)
              .join(', ')
          });
          setLogs2(prev => [
            `[UE-2] ${new Date().toLocaleTimeString()} | App: ${appName} | Pred: ${result.klass} (${result.confidence?.toFixed(2)})`,
            ...prev.slice(0, 49)
          ]);
        }

      } catch (err) {
        console.error("API Error:", err);
        // Optional: show error in UI
      }
    };

    // Poll every 3 seconds
    const interval = setInterval(() => {
      fetchPrediction(1);
      fetchPrediction(2);
    }, 3000);

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