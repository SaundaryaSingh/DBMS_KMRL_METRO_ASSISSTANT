import React, { useState, useEffect } from 'react';
import { RotateCcw, Play } from 'lucide-react';

export default function TransactionDemo() {
  const [logs, setLogs] = useState([]);
  const [finalState, setFinalState] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const resetTables = async () => {
    setLoading(true);
    try {
      await fetch('http://localhost:8000/api/transactions/reset', { method: 'POST' });
      setLogs(['Tables reset successfully to initial state.']);
      setFinalState(null);
    } catch (err) {
      console.error(err);
      setLogs(['Failed to reset tables']);
    }
    setLoading(false);
  };

  const runTransaction = async (id) => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/transactions/run/${id}`);
      const data = await res.json();
      if (!res.ok) {
        setLogs([`Error executing transaction: ${data.detail || 'Unknown error'}`]);
        setFinalState(null);
      } else {
        setLogs(data.logs || []);
        setFinalState(data.final_state || null);
      }
    } catch (err) {
      console.error(err);
      setLogs(['Error executing transaction (Network/Backend)']);
      setFinalState(null);
    }
    setLoading(false);
  };

  return (
    <div style={{ animation: 'fade-in 0.5s ease', display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1>Transaction Control (TCL)</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Demonstrating COMMIT, ROLLBACK, and SAVEPOINT</p>
        </div>
        <button className="btn btn-secondary" onClick={resetTables} disabled={loading}>
          <RotateCcw size={16} /> Reset DB State
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '2rem', flex: 1 }}>
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <h2>Simulations</h2>
          <button className="btn" onClick={() => runTransaction(1)} disabled={loading} style={{ justifyContent: 'center' }}>
            <Play size={16} /> Run Transaction 1
          </button>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Updates passenger, uses savepoints to insert multiple rows, then rolls back partially and commits.</p>
          
          <button className="btn" onClick={() => runTransaction(2)} disabled={loading} style={{ justifyContent: 'center' }}>
            <Play size={16} /> Run Transaction 2
          </button>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Updates ticket fare, inserts ticket, encounters error on next insert, rolls back to savepoint, commits.</p>
        </div>

        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <h2 style={{ marginBottom: '1rem' }}>Execution Logs</h2>
          <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px', flex: '0 0 auto', maxHeight: '200px', overflowY: 'auto', fontFamily: 'monospace', marginBottom: '2rem', color: '#a7f3d0' }}>
            {logs.length > 0 ? logs.map((log, i) => <div key={i}>{'>'} {log}</div>) : <div style={{ color: 'var(--text-secondary)' }}>No transaction executed yet.</div>}
            {loading && <div>{'>'} Executing...</div>}
          </div>

          <h2 style={{ marginBottom: '1rem' }}>Final Table State</h2>
          <div style={{ flex: 1, overflowY: 'auto' }}>
            {finalState ? (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      {Object.keys(finalState[0] || {}).map(key => (
                        <th key={key}>{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {finalState.map((row, i) => (
                      <tr key={i}>
                        {Object.values(row).map((val, j) => (
                          <td key={j}>{val}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '2rem' }}>Run a transaction to view final state</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
