import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

export default function AIChat() {
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Hello! I am the KMRL AI Assistant. I can help you query the database using natural language. Ask me about total passengers, average fares, stations by zone, or metro lines!' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endOfMessagesRef = useRef(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userQuery = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userQuery }]);
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userQuery })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'ai', text: data.response }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'ai', text: 'Sorry, I encountered an error connecting to the backend.' }]);
    }
    setLoading(false);
  };

  return (
    <div style={{ animation: 'fade-in 0.5s ease', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1>AI Assistant (RAG)</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Query the KMRL database using natural language.</p>
      </div>

      <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ display: 'flex', gap: '1rem', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
              <div style={{ 
                width: '40px', height: '40px', borderRadius: '50%', 
                background: msg.role === 'user' ? 'var(--accent-primary)' : 'rgba(255,255,255,0.1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center'
              }}>
                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} color="var(--accent-success)" />}
              </div>
              <div style={{
                background: msg.role === 'user' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255,255,255,0.05)',
                padding: '1rem 1.5rem',
                borderRadius: '16px',
                borderTopRightRadius: msg.role === 'user' ? '4px' : '16px',
                borderTopLeftRadius: msg.role === 'ai' ? '4px' : '16px',
                maxWidth: '75%',
                border: '1px solid rgba(255,255,255,0.05)'
              }}>
                {msg.text}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: 'flex', gap: '1rem' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Bot size={20} color="var(--accent-success)" />
              </div>
              <div style={{ padding: '1rem 1.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '16px', borderTopLeftRadius: '4px' }}>
                <span className="loader" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></span>
              </div>
            </div>
          )}
          <div ref={endOfMessagesRef} />
        </div>

        <form onSubmit={handleSend} style={{ display: 'flex', gap: '1rem', padding: '1.5rem', borderTop: '1px solid var(--border-color)', marginTop: 'auto' }}>
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about total passengers, average fares..."
            style={{
              flex: 1,
              background: 'rgba(0,0,0,0.2)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '1rem 1.5rem',
              color: 'white',
              fontSize: '1rem',
              outline: 'none'
            }}
          />
          <button type="submit" className="btn" disabled={loading || !input.trim()}>
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}
