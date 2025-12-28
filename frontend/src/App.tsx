import React from 'react';
import { fetchJson, type JsonValue } from './api';

type Mode = 'oneway' | 'roundtrip';

export function App() {
  const [mode, setMode] = React.useState<Mode>('oneway');
  const [startDate, setStartDate] = React.useState<string>('');
  const [endDate, setEndDate] = React.useState<string>('');
  const [n, setN] = React.useState<number>(1);
  const [deepness, setDeepness] = React.useState<number>(1);

  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [result, setResult] = React.useState<JsonValue | null>(null);

  async function runHealth() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await fetchJson<JsonValue>('/api/health');
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  async function runSearch() {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const path = mode === 'oneway' ? '/api/flights/oneway' : '/api/flights/roundtrip';
      const data = await fetchJson<JsonValue>(path, {
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        n,
        deepness
      });
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: '40px auto', padding: 16, fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ marginTop: 0 }}>Flight Alerts</h1>

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 16 }}>
        <button onClick={runHealth} disabled={loading}>
          Check /api/health
        </button>

        <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          Mode
          <select value={mode} onChange={(e) => setMode(e.target.value as Mode)} disabled={loading}>
            <option value="oneway">oneway</option>
            <option value="roundtrip">roundtrip</option>
          </select>
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          start_date
          <input value={startDate} onChange={(e) => setStartDate(e.target.value)} placeholder="YYYY-MM-DD" />
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          end_date
          <input value={endDate} onChange={(e) => setEndDate(e.target.value)} placeholder="YYYY-MM-DD" />
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          n
          <input
            type="number"
            min={1}
            value={n}
            onChange={(e) => setN(Number(e.target.value))}
            style={{ width: 80 }}
          />
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          deepness
          <input
            type="number"
            min={1}
            value={deepness}
            onChange={(e) => setDeepness(Number(e.target.value))}
            style={{ width: 80 }}
          />
        </label>

        <button onClick={runSearch} disabled={loading}>
          Call {mode === 'oneway' ? '/api/flights/oneway' : '/api/flights/roundtrip'}
        </button>
      </div>

      {loading ? <p>Loading…</p> : null}
      {error ? (
        <pre style={{ background: '#fee', padding: 12, overflowX: 'auto' }}>{error}</pre>
      ) : null}
      {result !== null ? (
        <pre style={{ background: '#f6f8fa', padding: 12, overflowX: 'auto' }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      ) : null}

      <p style={{ marginTop: 16, color: '#666' }}>
        Assumption: the backend endpoints return JSON.
      </p>
    </div>
  );
}
