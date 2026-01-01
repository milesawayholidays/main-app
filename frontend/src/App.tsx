import React from 'react';
import { fetchJson, type JsonValue } from './api';
import { DateRangeField, type CompleteDateRange } from './components/DateRangeField';
import { FlightOptionsTable } from './components/FlightOptionsTable';
import { TextField } from './components/TextField';

type Mode = 'oneway' | 'roundtrip';

const N_MAX = 8;
const DEEPNESS_MAX = 3;

const REGION_OPTIONS = ['North America', 'South America', 'Africa', 'Asia', 'Europe', 'Oceania'] as const;
const CABIN_OPTIONS = ['economy', 'premium', 'business', 'first'] as const;
const SOURCE_OPTIONS = ['azul', 'smiles', 'qantas'] as const;

function clampInt(value: unknown, min: number, max: number, fallback = min) {
  const n = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(n)) return fallback;
  const rounded = Math.trunc(n);
  return Math.min(max, Math.max(min, rounded));
}

export function App() {
  const [mode, setMode] = React.useState<Mode>('oneway');
  const [dateRange, setDateRange] = React.useState<CompleteDateRange | null>(null);
  const [n, setN] = React.useState<number>(1);
  const [deepness, setDeepness] = React.useState<number>(1);

  const [originRegions, setOriginRegions] = React.useState<string[]>([]);
  const [destinationRegions, setDestinationRegions] = React.useState<string[]>([]);
  const [originCountries, setOriginCountries] = React.useState<string>('');
  const [destinationCountries, setDestinationCountries] = React.useState<string>('');
  const [originCities, setOriginCities] = React.useState<string>('');
  const [destinationCities, setDestinationCities] = React.useState<string>('');
  const [originAirports, setOriginAirports] = React.useState<string>('');
  const [destinationAirports, setDestinationAirports] = React.useState<string>('');
  const [sources, setSources] = React.useState<string[]>([]);
  const [cabins, setCabins] = React.useState<string[]>([]);
  const [minCost, setMinCost] = React.useState<string>('');
  const [maxCost, setMaxCost] = React.useState<string>('');
  const [minRemainingSeats, setMinRemainingSeats] = React.useState<string>('');
  const [minReturnDays, setMinReturnDays] = React.useState<string>('');
  const [maxReturnDays, setMaxReturnDays] = React.useState<string>('');

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

      const start_date = dateRange ? formatDateYYYYMMDD(dateRange.from) : undefined;
      const end_date = dateRange ? formatDateYYYYMMDD(dateRange.to) : undefined;

      const origin_regions = originRegions.length ? originRegions : undefined;
      const destination_regions = destinationRegions.length ? destinationRegions : undefined;
      const origin_countries = parseCommaList(originCountries);
      const destination_countries = parseCommaList(destinationCountries);
      const origin_cities = parseCommaList(originCities);
      const destination_cities = parseCommaList(destinationCities);
      const origin_airports = parseCommaList(originAirports);
      const destination_airports = parseCommaList(destinationAirports);
      const sources_list = sources.length ? sources : undefined;
      const cabins_list = cabins.length ? cabins : undefined;

      const parsedMinCost = parseNumberOrNull(minCost);
      const parsedMaxCost = parseNumberOrNull(maxCost);
      const parsedMinRemainingSeats = parseIntOrNull(minRemainingSeats);
      const parsedMinReturnDays = parseIntOrNull(minReturnDays);
      const parsedMaxReturnDays = parseIntOrNull(maxReturnDays);

      const data = await fetchJson<JsonValue>(path, {
        start_date,
        end_date,
        n,
        deepness,
        origin_regions,
        destination_regions,
        origin_countries,
        destination_countries,
        origin_cities,
        destination_cities,
        origin_airports,
        destination_airports,
        sources: sources_list,
        cabins: cabins_list,
        min_cost: parsedMinCost ?? undefined,
        max_cost: parsedMaxCost ?? undefined,
        min_remaining_seats: parsedMinRemainingSeats ?? undefined,
        min_return_days: mode === 'roundtrip' ? parsedMinReturnDays ?? undefined : undefined,
        max_return_days: mode === 'roundtrip' ? parsedMaxReturnDays ?? undefined : undefined
      });
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  function loadSampleResult() {
    setLoading(false);
    setError(null);
    setResult(SAMPLE_FLIGHT_OPTIONS_RESULT);
  }

  return (
    <div style={{ maxWidth: 1400, margin: '40px auto', padding: 16, fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
        <h1 style={{ marginTop: 0, marginBottom: 0 }}>Flight Alerts</h1>

        <button onClick={runHealth} disabled={loading}>
          Check api health
        </button>
      </div>

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 16, marginBottom: 16 }}>

        <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          Mode
          <select value={mode} onChange={(e) => setMode(e.target.value as Mode)} disabled={loading}>
            <option value="oneway">oneway</option>
            <option value="roundtrip">roundtrip</option>
          </select>
        </label>

        <DateRangeField label="Dates" value={dateRange} onChange={setDateRange} disabled={loading} />

        <TextField
          label="number of results per region pair (n)"
          type="number"
          min={1}
          max={N_MAX}
          value={n}
          onChange={(value) => setN(clampInt(value, 1, N_MAX, 1))}
          inputStyle={{ width: 80 }}
        />

        <TextField
          label="complexity of search (deepness)"
          type="number"
          min={1}
          max={DEEPNESS_MAX}
          value={deepness}
          onChange={(value) => setDeepness(clampInt(value, 1, DEEPNESS_MAX, 1))}
          inputStyle={{ width: 80 }}
        />

        <details style={{ border: '1px solid #ddd', borderRadius: 6, padding: '6px 10px' }}>
          <summary style={{ cursor: 'pointer', userSelect: 'none' }}>Queries</summary>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center', marginTop: 10 }}>
            <CheckboxDropdown
              label="Origin regions"
              options={REGION_OPTIONS}
              selected={originRegions}
              onChange={setOriginRegions}
              disabled={loading}
            />
            <CheckboxDropdown
              label="Destination regions"
              options={REGION_OPTIONS}
              selected={destinationRegions}
              onChange={setDestinationRegions}
              disabled={loading}
            />

            <TextField
              label="Origin countries"
              value={originCountries}
              onChange={setOriginCountries}
              placeholder="e.g. BR, US"
              inputStyle={{ width: 160 }}
            />
            <TextField
              label="Destination countries"
              value={destinationCountries}
              onChange={setDestinationCountries}
              placeholder="e.g. FR, GB"
              inputStyle={{ width: 160 }}
            />

            <TextField
              label="Origin cities"
              value={originCities}
              onChange={setOriginCities}
              placeholder="e.g. Sao Paulo"
              inputStyle={{ width: 200 }}
            />
            <TextField
              label="Destination cities"
              value={destinationCities}
              onChange={setDestinationCities}
              placeholder="e.g. Paris"
              inputStyle={{ width: 200 }}
            />

            <TextField
              label="Origin airports"
              value={originAirports}
              onChange={setOriginAirports}
              placeholder="e.g. GRU, GIG"
              inputStyle={{ width: 160 }}
            />
            <TextField
              label="Destination airports"
              value={destinationAirports}
              onChange={setDestinationAirports}
              placeholder="e.g. CDG, LHR"
              inputStyle={{ width: 160 }}
            />

            <CheckboxDropdown
              label="Sources"
              options={SOURCE_OPTIONS}
              selected={sources}
              onChange={setSources}
              disabled={loading}
            />
            <CheckboxDropdown
              label="Cabins"
              options={CABIN_OPTIONS}
              selected={cabins}
              onChange={setCabins}
              disabled={loading}
            />

            <TextField
              label="Min cost"
              type="number"
              step={1}
              value={minCost}
              onChange={setMinCost}
              placeholder="0"
              inputStyle={{ width: 90 }}
            />
            <TextField
              label="Max cost"
              type="number"
              step={1}
              value={maxCost}
              onChange={setMaxCost}
              placeholder="999999"
              inputStyle={{ width: 90 }}
            />
            <TextField
              label="Min remaining seats"
              type="number"
              min={0}
              step={1}
              value={minRemainingSeats}
              onChange={setMinRemainingSeats}
              placeholder="0"
              inputStyle={{ width: 70 }}
            />

            {mode === 'roundtrip' ? (
              <>
                <TextField
                  label="Min return days"
                  type="number"
                  min={0}
                  step={1}
                  value={minReturnDays}
                  onChange={setMinReturnDays}
                  placeholder="0"
                  inputStyle={{ width: 70 }}
                />
                <TextField
                  label="Max return days"
                  type="number"
                  min={0}
                  step={1}
                  value={maxReturnDays}
                  onChange={setMaxReturnDays}
                  placeholder="30"
                  inputStyle={{ width: 70 }}
                />
              </>
            ) : null}
          </div>
        </details>

        <button onClick={runSearch} disabled={loading}>
          Search
        </button>

        <button type="button" onClick={loadSampleResult} disabled={loading}>
          Load sample result
        </button>
      </div>

      {loading ? <p>Loading…</p> : null}
      {error ? (
        <pre style={{ background: '#fee', padding: 12, overflowX: 'auto' }}>{error}</pre>
      ) : null}
      {result !== null ? (
        <FlightOptionsTable value={result} />
      ) : null}
    </div>
  );
}

function formatDateYYYYMMDD(date: Date) {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

function parseCommaList(input: string): string[] | undefined {
  const parts = input
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
  return parts.length ? parts : undefined;
}

function CheckboxDropdown({
  label,
  options,
  selected,
  onChange,
  disabled
}: {
  label: string;
  options: readonly string[];
  selected: string[];
  onChange: (next: string[]) => void;
  disabled?: boolean;
}) {
  const id = React.useId();
  const rootRef = React.useRef<HTMLDivElement | null>(null);
  const [open, setOpen] = React.useState(false);

  const selectedSet = React.useMemo(() => new Set(selected), [selected]);

  React.useEffect(() => {
    if (!open) return;

    function onDocMouseDown(e: MouseEvent) {
      const root = rootRef.current;
      if (!root) return;
      if (e.target instanceof Node && !root.contains(e.target)) setOpen(false);
    }

    function onDocKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false);
    }

    document.addEventListener('mousedown', onDocMouseDown);
    document.addEventListener('keydown', onDocKeyDown);
    return () => {
      document.removeEventListener('mousedown', onDocMouseDown);
      document.removeEventListener('keydown', onDocKeyDown);
    };
  }, [open]);

  function toggle(value: string) {
    const next = new Set(selectedSet);
    if (next.has(value)) next.delete(value);
    else next.add(value);
    onChange(Array.from(next));
  }

  const summaryText = selected.length ? `${label} (${selected.length})` : `${label} (all)`;

  return (
    <div
      ref={rootRef}
      style={{ position: 'relative', minWidth: 220 }}
      aria-label={label}
    >
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={id}
        disabled={disabled}
        onClick={() => setOpen((v) => !v)}
        style={{
          width: '100%',
          textAlign: 'left',
          border: '1px solid #ddd',
          borderRadius: 6,
          padding: '6px 10px',
          background: 'transparent',
          cursor: disabled ? 'not-allowed' : 'pointer',
          opacity: disabled ? 0.6 : 1
        }}
      >
        {summaryText}
      </button>

      {open ? (
        <div
          id={id}
          role="menu"
          style={{
            position: 'absolute',
            top: 'calc(100% + 6px)',
            left: 0,
            zIndex: 1000,
            border: '1px solid #ddd',
            borderRadius: 6,
            background: '#fff',
            padding: 10,
            minWidth: 260,
            maxHeight: 260,
            overflow: 'auto'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
            <div style={{ fontWeight: 600 }}>{label}</div>
            <button type="button" onClick={() => setOpen(false)} disabled={disabled}>
              Close
            </button>
          </div>

          <div style={{ marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button type="button" onClick={() => onChange([])} disabled={disabled}>
              Clear (all)
            </button>
            <button type="button" onClick={() => onChange([...options])} disabled={disabled}>
              Select all
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 10 }}>
            {options.map((opt) => (
              <label key={opt} style={{ display: 'flex', alignItems: 'center', gap: 8, opacity: disabled ? 0.6 : 1 }}>
                <input
                  type="checkbox"
                  checked={selectedSet.has(opt)}
                  onChange={() => toggle(opt)}
                  disabled={disabled}
                />
                {opt}
              </label>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function parseNumberOrNull(input: string): number | null {
  const trimmed = input.trim();
  if (!trimmed) return null;
  const n = Number(trimmed);
  return Number.isFinite(n) ? n : null;
}

function parseIntOrNull(input: string): number | null {
  const trimmed = input.trim();
  if (!trimmed) return null;
  const n = Number.parseInt(trimmed, 10);
  return Number.isFinite(n) ? n : null;
}

const SAMPLE_FLIGHT_OPTIONS_RESULT: JsonValue = {
  status: 200,
  data: {
    single_trips: [
      {
        region: 'Africa',
        origin_city: 'Johannesburg',
        destination_city: 'London',
        origin_airport: 'JNB',
        destination_airport: 'LHR',
        cabin: 'business',
        source: 'seats.aero',
        departure_date: '2026-01-12',
        mileage_cost: 95000,
        normal_taxes: 68500,
        normal_total_cost: 291500
      },
      {
        region: 'Europe',
        origin_city: 'London',
        destination_city: 'Johannesburg',
        origin_airport: 'LHR',
        destination_airport: 'JNB',
        cabin: 'business',
        source: 'seats.aero',
        departure_date: '2026-01-19',
        mileage_cost: 95000,
        normal_taxes: 70200,
        normal_total_cost: 294200
      },
      {
        region: 'North America',
        origin_city: 'New York',
        destination_city: 'Paris',
        origin_airport: 'JFK',
        destination_airport: 'CDG',
        cabin: 'economy',
        source: 'seats.aero',
        departure_date: '2026-02-03',
        mileage_cost: 30000,
        normal_taxes: 19800,
        normal_total_cost: 131800
      }
    ],
    round_trips: [
      {
        region: 'Africa-Europe',
        // For round trips the backend may include total_cost fields directly,
        // but the frontend also knows how to sum outbound+return costs.
        normal_total_cost: 585700,
        outbound: {
          region: 'Africa',
          origin_city: 'Johannesburg',
          destination_city: 'London',
          origin_airport: 'JNB',
          destination_airport: 'LHR',
          cabin: 'business',
          departure_date: '2026-01-12',
          mileage_cost: 95000,
          normal_taxes: 68500,
          normal_total_cost: 291500
        },
        return_: {
          region: 'Europe',
          origin_city: 'London',
          destination_city: 'Johannesburg',
          origin_airport: 'LHR',
          destination_airport: 'JNB',
          cabin: 'business',
          departure_date: '2026-01-19',
          mileage_cost: 95000,
          normal_taxes: 70200,
          normal_total_cost: 294200
        }
      }
    ],
    round_options: [
      {
        ID: 'opt-1',
        region: 'Africa-Europe',
        origin_city: 'Johannesburg',
        destination_city: 'London',
        origin_country: 'ZA',
        destination_country: 'GB',
        cabin: 'business',
        departure_dates: ['2026-01-10', '2026-01-12', '2026-01-14'],
        return_dates: ['2026-01-17', '2026-01-19', '2026-01-21'],
        lowest_mileage_cost: 180000,
        highest_mileage_cost: 210000,
        average_mileage_cost: 190000,
        lowest_taxes: 132000,
        highest_taxes: 160000,
        average_taxes: 145000,
        lowest_total_cost: 510000,
        highest_total_cost: 650000,
        average_total_cost: 585000
      },
      {
        ID: 'opt-2',
        region: 'North America-Europe',
        origin_city: 'New York',
        destination_city: 'Paris',
        origin_country: 'US',
        destination_country: 'FR',
        cabin: 'economy',
        departure_dates: ['2026-02-01', '2026-02-03'],
        return_dates: ['2026-02-08', '2026-02-10'],
        lowest_mileage_cost: 50000,
        highest_mileage_cost: 70000,
        average_mileage_cost: 60000,
        lowest_taxes: 38000,
        highest_taxes: 52000,
        average_taxes: 45000,
        lowest_total_cost: 240000,
        highest_total_cost: 310000,
        average_total_cost: 275000
      }
    ]
  }
};
