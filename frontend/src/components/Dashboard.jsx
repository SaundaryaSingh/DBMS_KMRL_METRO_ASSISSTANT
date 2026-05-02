import React, { useEffect, useState } from 'react';
import { Users, Train, MapPin, Activity } from 'lucide-react';

export default function Dashboard() {
  const [data, setData] = useState({ lines: [], stations: [], trains: [], passengers: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/queries/dashboard-data')
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch dashboard data", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', marginTop: '4rem' }}><span className="loader"></span></div>;

  return (
    <div style={{ animation: 'fade-in 0.5s ease' }}>
      <h1>System Overview</h1>
      
      <div className="grid" style={{ marginBottom: '3rem' }}>
        <div className="glass-panel stat-card">
          <div className="stat-icon"><Activity /></div>
          <div className="stat-info">
            <h3>Active Lines</h3>
            <p>{data.lines.length}</p>
          </div>
        </div>
        <div className="glass-panel stat-card">
          <div className="stat-icon"><MapPin /></div>
          <div className="stat-info">
            <h3>Stations</h3>
            <p>{data.stations.length}</p>
          </div>
        </div>
        <div className="glass-panel stat-card">
          <div className="stat-icon"><Train /></div>
          <div className="stat-info">
            <h3>Trains</h3>
            <p>{data.trains.length}</p>
          </div>
        </div>
        <div className="glass-panel stat-card">
          <div className="stat-icon"><Users /></div>
          <div className="stat-info">
            <h3>Passengers</h3>
            <p>{data.passengers.length}</p>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <div className="glass-panel">
          <h2 style={{ fontSize: '1.4rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1rem' }}>Metro Lines</h2>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Line Name</th>
                  <th>Total Stations</th>
                </tr>
              </thead>
              <tbody>
                {data.lines.map((line, i) => (
                  <tr key={i}>
                    <td>
                      <span className="badge badge-primary">{line.line_name}</span>
                    </td>
                    <td>{line.total_stations}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="glass-panel">
          <h2 style={{ fontSize: '1.4rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1rem' }}>Recent Passengers</h2>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Age</th>
                  <th>Gender</th>
                </tr>
              </thead>
              <tbody>
                {data.passengers.slice(0, 5).map((p, i) => (
                  <tr key={i}>
                    <td>{p.name}</td>
                    <td>{p.age}</td>
                    <td>{p.gender}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
