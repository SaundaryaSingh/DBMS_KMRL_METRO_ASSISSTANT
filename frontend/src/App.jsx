import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, Database, MessageSquare, ArrowRightLeft, TrainFront } from 'lucide-react';
import Dashboard from './components/Dashboard';
import QueryShowcase from './components/QueryShowcase';
import AIChat from './components/AIChat';
import TransactionDemo from './components/TransactionDemo';
import './index.css';

function Sidebar() {
  return (
    <div className="sidebar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
        <div style={{ background: 'var(--accent-primary)', padding: '0.5rem', borderRadius: '10px', display: 'flex' }}>
          <TrainFront color="white" size={24} />
        </div>
        <h2 style={{ margin: 0, fontSize: '1.4rem', background: 'none', WebkitTextFillColor: 'initial', WebkitBackgroundClip: 'initial' }}>KMRL Metro</h2>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <NavLink to="/" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
          <LayoutDashboard size={20} />
          Dashboard
        </NavLink>
        <NavLink to="/queries" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
          <Database size={20} />
          Query Showcase
        </NavLink>
        <NavLink to="/transactions" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
          <ArrowRightLeft size={20} />
          Transactions
        </NavLink>
        <NavLink to="/ai-chat" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
          <MessageSquare size={20} />
          AI Assistant
        </NavLink>
      </nav>

      <div style={{ marginTop: 'auto', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '12px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
        <p>AI-Integrated Intelligent Metro Information System</p>
        <p style={{ marginTop: '0.5rem', fontWeight: 'bold' }}>Saundarya & Nehal</p>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/queries" element={<QueryShowcase />} />
            <Route path="/transactions" element={<TransactionDemo />} />
            <Route path="/ai-chat" element={<AIChat />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
