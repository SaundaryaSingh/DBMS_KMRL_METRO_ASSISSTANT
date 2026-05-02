import React, { useState } from 'react';
import { Play } from 'lucide-react';

const QUERIES = [
  { id: 'aggregate/total-passengers', title: 'Total Passengers (Aggregate)', desc: 'Find the total number of registered passengers.', sql: 'SELECT COUNT(*) AS Total_Passengers FROM Passenger;' },
  { id: 'aggregate/average-fare', title: 'Average Fare (Aggregate)', desc: 'Calculate the average fare between stations.', sql: 'SELECT AVG(fare_amount) AS Avg_Fare FROM Fare;' },
  { id: 'aggregate/stations-per-zone', title: 'Stations per Zone (Aggregate)', desc: 'Find how many stations are present in each zone (where > 2).', sql: 'SELECT zone, COUNT(*) AS Station_Count FROM Station GROUP BY zone HAVING COUNT(*) > 2;' },
  { id: 'sets/station-facilities-unique', title: 'Station Names & Facilities (Sets - UNION)', desc: 'Displays a combined list of station names and facilities without duplicates.', sql: 'SELECT station_name FROM Station UNION SELECT facility_name FROM Station_Facility;' },
  { id: 'sets/station-facilities-all', title: 'All Station Names & Facilities (Sets - UNION ALL)', desc: 'Displays all station names and facilities including duplicates.', sql: 'SELECT station_name FROM Station UNION ALL SELECT facility_name FROM Station_Facility;' },
  { id: 'subqueries/fares-above-average', title: 'Fares Above Average (Subquery)', desc: 'Identifies fares that are higher than the average fare.', sql: 'SELECT * FROM Fare WHERE fare_amount > (SELECT AVG(fare_amount) FROM Fare);' },
  { id: 'subqueries/passengers-with-tickets', title: 'Passengers with Tickets (Subquery)', desc: 'Retrieves passengers who have booked tickets.', sql: 'SELECT * FROM Passenger WHERE passenger_id IN (SELECT passenger_id FROM Ticket);' },
  { id: 'joins/passenger-tickets', title: 'Passenger Ticket IDs (Joins)', desc: 'Displays passenger names along with their ticket IDs.', sql: 'SELECT p.name, t.ticket_id FROM Passenger p INNER JOIN Ticket t ON p.passenger_id = t.passenger_id;' },
  { id: 'joins/station-fares', title: 'Stations with Fare Details (Joins)', desc: 'Shows all stations along with their fare details if available.', sql: 'SELECT s.station_name, f.fare_amount FROM Station s LEFT JOIN Fare f ON s.station_id = f.source_station_id;' },
  { id: 'views/high-fare', title: 'High Fare Records (Views)', desc: 'Displays all records from the HighFare view.', sql: 'SELECT * FROM HighFare;' },
  { id: 'cursors/get-passengers', title: 'Get Passengers (Cursors/Procedures)', desc: 'Executes the procedure to display passenger details.', sql: 'CALL GetPassengers();' }
];

export default function QueryShowcase() {
  const [activeQuery, setActiveQuery] = useState(QUERIES[0]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const runQuery = async (query) => {
    setActiveQuery(query);
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/queries/${query.id}`);
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error(err);
      setResults([{ error: 'Failed to execute query' }]);
    }
    setLoading(false);
  };

  return (
    <div style={{ animation: 'fade-in 0.5s ease', display: 'flex', gap: '2rem', height: 'calc(100vh - 4rem)' }}>
      <div className="glass-panel" style={{ width: '350px', display: 'flex', flexDirection: 'column', gap: '1rem', overflowY: 'auto' }}>
        <h2 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>SQL Queries</h2>
        {QUERIES.map(q => (
          <div 
            key={q.id}
            onClick={() => { setActiveQuery(q); setResults(null); }}
            style={{ 
              padding: '1rem', 
              borderRadius: '8px', 
              background: activeQuery?.id === q.id ? 'rgba(59, 130, 246, 0.15)' : 'rgba(255,255,255,0.02)',
              border: activeQuery?.id === q.id ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid transparent',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <h4 style={{ color: activeQuery?.id === q.id ? 'var(--accent-primary)' : 'var(--text-primary)', marginBottom: '0.25rem' }}>{q.title}</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{q.desc}</p>
          </div>
        ))}
      </div>

      <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {activeQuery ? (
          <>
            <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '1.5rem', marginBottom: '1.5rem' }}>
              <h2>{activeQuery.title}</h2>
              <p style={{ color: 'var(--text-secondary)' }}>{activeQuery.desc}</p>
              
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px', fontFamily: 'monospace', color: '#a7f3d0', marginTop: '1rem', marginBottom: '1rem', border: '1px solid rgba(255,255,255,0.05)' }}>
                {activeQuery.sql}
              </div>

              <button className="btn" onClick={() => runQuery(activeQuery)}>
                <Play size={16} /> Execute Query
              </button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto' }}>
              {loading ? (
                <div style={{ display: 'flex', justifyContent: 'center', marginTop: '2rem' }}><span className="loader"></span></div>
              ) : results ? (
                results.length > 0 ? (
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          {Object.keys(results[0]).map(key => (
                            <th key={key}>{key.replace(/_/g, ' ')}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {results.map((row, i) => (
                          <tr key={i}>
                            {Object.values(row).map((val, j) => (
                              <td key={j}>{val === null ? 'NULL' : String(val)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>No results found</div>
                )
              ) : (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Select a query to view results</div>
              )}
            </div>
          </>
        ) : (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)', margin: 'auto' }}>Select a query from the left panel</div>
        )}
      </div>
    </div>
  );
}
