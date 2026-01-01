import * as React from 'react';
import { fetchJson } from '../api';
import { buildFlightOptionsTableModel } from '../flightOptionsTableModel';

export type FlightOptionsTableProps = {
  value: unknown;
};

type SelectedRoute = {
  origin: string;
  destination: string;
  cabin: string | null;
};

export function FlightOptionsTable({ value }: FlightOptionsTableProps) {
  const model = React.useMemo(() => buildFlightOptionsTableModel(value), [value]);
  const [regionPair, setRegionPair] = React.useState<string>('');
  const [originCountry, setOriginCountry] = React.useState<string>('');
  const [destinationCountry, setDestinationCountry] = React.useState<string>('');
  const [originAirport, setOriginAirport] = React.useState<string>('');
  const [destinationAirport, setDestinationAirport] = React.useState<string>('');
  const [program, setProgram] = React.useState<string>('');
  const [origin, setOrigin] = React.useState<string>('');
  const [destination, setDestination] = React.useState<string>('');
  const [cabin, setCabin] = React.useState<string>('');
  const [minTotalCost, setMinTotalCost] = React.useState<string>('');
  const [maxTotalCost, setMaxTotalCost] = React.useState<string>('');

  const [selectedRoute, setSelectedRoute] = React.useState<SelectedRoute | null>(null);

  const [toggledRowIds, setToggledRowIds] = React.useState<Set<string>>(() => new Set());

  const [postLoading, setPostLoading] = React.useState(false);
  const [postError, setPostError] = React.useState<string | null>(null);
  const [postResult, setPostResult] = React.useState<string | null>(null);

  // When new results arrive, keep toggles that still exist; drop stale ones.
  React.useEffect(() => {
    const allIds = new Set<string>();
    for (const r of model.rows) allIds.add(r.id);
    for (const r of model.singleRows) allIds.add(r.id);

    setToggledRowIds((prev) => {
      if (prev.size === 0) return prev;
      const next = new Set<string>();
      for (const id of prev) if (allIds.has(id)) next.add(id);
      return next;
    });
  }, [model.rows, model.singleRows]);

  const inDrilldown = model.view === 'round' && selectedRoute !== null;
  const showReturn = model.view === 'round' && !inDrilldown;

  const rowsForFilterOptions = React.useMemo(() => {
    if (inDrilldown) return [];
    if (!regionPair) return model.rows;
    return model.rows.filter((r) => r.regionPair === regionPair);
  }, [model.rows, regionPair, inDrilldown]);

  const filterOptions = React.useMemo(() => {
    const originCountries = new Set<string>();
    const destinationCountries = new Set<string>();
    const originAirports = new Set<string>();
    const destinationAirports = new Set<string>();
    const programs = new Set<string>();
    const origins = new Set<string>();
    const destinations = new Set<string>();
    const cabins = new Set<string>();

    for (const r of rowsForFilterOptions) {
      if (r.originCountry) originCountries.add(r.originCountry);
      if (r.destinationCountry) destinationCountries.add(r.destinationCountry);
      if (r.originAirport) originAirports.add(r.originAirport);
      if (r.destinationAirport) destinationAirports.add(r.destinationAirport);
      if (r.program) programs.add(r.program);
      if (r.origin) origins.add(r.origin);
      if (r.destination) destinations.add(r.destination);
      if (r.cabin) cabins.add(r.cabin);
    }

    return {
      originCountries: Array.from(originCountries).sort((a, b) => a.localeCompare(b)),
      destinationCountries: Array.from(destinationCountries).sort((a, b) => a.localeCompare(b)),
      originAirports: Array.from(originAirports).sort((a, b) => a.localeCompare(b)),
      destinationAirports: Array.from(destinationAirports).sort((a, b) => a.localeCompare(b)),
      programs: Array.from(programs).sort((a, b) => a.localeCompare(b)),
      origins: Array.from(origins).sort((a, b) => a.localeCompare(b)),
      destinations: Array.from(destinations).sort((a, b) => a.localeCompare(b)),
      cabins: Array.from(cabins).sort((a, b) => a.localeCompare(b))
    };
  }, [rowsForFilterOptions]);

  React.useEffect(() => {
    if (originCountry && !filterOptions.originCountries.includes(originCountry)) setOriginCountry('');
    if (destinationCountry && !filterOptions.destinationCountries.includes(destinationCountry)) setDestinationCountry('');
    if (originAirport && !filterOptions.originAirports.includes(originAirport)) setOriginAirport('');
    if (destinationAirport && !filterOptions.destinationAirports.includes(destinationAirport)) setDestinationAirport('');
    if (program && !filterOptions.programs.includes(program)) setProgram('');
    if (origin && !filterOptions.origins.includes(origin)) setOrigin('');
    if (destination && !filterOptions.destinations.includes(destination)) setDestination('');
    if (cabin && !filterOptions.cabins.includes(cabin)) setCabin('');
  }, [
    originCountry,
    destinationCountry,
    originAirport,
    destinationAirport,
    program,
    origin,
    destination,
    cabin,
    filterOptions
  ]);

  function parsePriceToCents(input: string): number | null {
    const trimmed = input.trim();
    if (!trimmed) return null;
    // Accept both "1234,56" and "1234.56". Also tolerate "1.234,56".
    const normalized = trimmed.replace(/\./g, '').replace(',', '.');
    const parsed = Number.parseFloat(normalized);
    if (!Number.isFinite(parsed)) return null;
    return Math.round(parsed * 100);
  }

  const minCents = React.useMemo(() => parsePriceToCents(minTotalCost), [minTotalCost]);
  const maxCents = React.useMemo(() => parsePriceToCents(maxTotalCost), [maxTotalCost]);

  const rows = React.useMemo(() => {
    if (inDrilldown && selectedRoute) {
      return model.singleRows.filter((r) => {
        if (r.origin !== selectedRoute.origin) return false;
        if (r.destination !== selectedRoute.destination) return false;
        return true;
      });
    }

    return model.rows.filter((r) => {
      if (regionPair && r.regionPair !== regionPair) return false;
      if (originCountry && r.originCountry !== originCountry) return false;
      if (destinationCountry && r.destinationCountry !== destinationCountry) return false;
      if (originAirport && r.originAirport !== originAirport) return false;
      if (destinationAirport && r.destinationAirport !== destinationAirport) return false;
      if (program && r.program !== program) return false;
      if (origin && r.origin !== origin) return false;
      if (destination && r.destination !== destination) return false;
      if (cabin && r.cabin !== cabin) return false;

      if (minCents !== null) {
        if (r.totalCostCents === null) return false;
        if (r.totalCostCents < minCents) return false;
      }
      if (maxCents !== null) {
        if (r.totalCostCents === null) return false;
        if (r.totalCostCents > maxCents) return false;
      }

      return true;
    });
  }, [
    model.rows,
    model.singleRows,
    regionPair,
    originCountry,
    destinationCountry,
    originAirport,
    destinationAirport,
    program,
    origin,
    destination,
    cabin,
    minCents,
    maxCents,
    inDrilldown,
    selectedRoute
  ]);

  const toggledRows = React.useMemo(() => {
    if (toggledRowIds.size === 0) return [];
    const byId = new Map<string, typeof model.rows[number]>();
    for (const r of model.rows) byId.set(r.id, r);
    for (const r of model.singleRows) byId.set(r.id, r);
    const out: Array<typeof model.rows[number]> = [];
    for (const id of toggledRowIds) {
      const row = byId.get(id);
      if (row) out.push(row);
    }
    return out;
  }, [toggledRowIds, model.rows, model.singleRows]);

  async function generatePostFromToggles() {
    setPostLoading(true);
    setPostError(null);
    setPostResult(null);

    try {
      const payload = {
        rows: toggledRows.map((r) => ({
          id: r.id,
          origin_city: r.origin ?? undefined,
          origin_country: r.originCountry ?? undefined,
          destination_city: r.destination ?? undefined,
          destination_country: r.destinationCountry ?? undefined,
          departure_date: r.outboundDates ?? undefined,
          return_date: r.returnDates ?? undefined,
          cabin: r.cabin ?? undefined,
          program: r.program ?? undefined,
          mileage_cost: r.mileageCost ?? undefined,
          taxes: r.taxes ?? undefined,
          total_cost: r.totalCost ?? undefined
        }))
      };

      const res = await fetchJson<any>('/api/get-post', undefined, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      // Accept either direct or wrapped payload shapes.
      const data = res?.data ?? res;
      const posts: Array<{ id?: string; post?: string }> = data?.posts ?? [];
      const skipped: Array<{ id?: string; reason?: string }> = data?.skipped ?? [];

      const textParts: string[] = [];
      for (const p of posts) {
        if (p.post) textParts.push(p.post);
      }
      if (skipped.length) {
        textParts.push(
          '\n---\nSkipped:\n' +
            skipped.map((s) => `- ${s.id ?? '(no id)'}: ${s.reason ?? 'unknown'}`).join('\n')
        );
      }

      setPostResult(textParts.join('\n\n---\n\n'));
    } catch (e) {
      setPostError(e instanceof Error ? e.message : String(e));
    } finally {
      setPostLoading(false);
    }
  }

  function handleRoundRowClick(r: (typeof model.rows)[number]) {
    if (model.view !== 'round') return;
    if (!r.origin || !r.destination) return;
    setSelectedRoute({
      origin: r.origin,
      destination: r.destination,
      cabin: r.cabin
    });
  }

  function toggleRow(id: string) {
    setToggledRowIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  if (model.rows.length === 0) {
    return (
      <pre style={{ background: '#f6f8fa', padding: 12, overflowX: 'auto' }}>
        {JSON.stringify(value, null, 2)}
      </pre>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {inDrilldown && selectedRoute ? (
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <button type="button" onClick={() => setSelectedRoute(null)}>
            Back
          </button>
          <button
            type="button"
            onClick={generatePostFromToggles}
            disabled={postLoading || toggledRows.length === 0}
          >
            {postLoading ? 'Generating…' : `Generate post (${toggledRows.length})`}
          </button>
          <div style={{ fontSize: 14, opacity: 0.9 }}>
            Showing oneways for: {selectedRoute.origin} → {selectedRoute.destination}
            {selectedRoute.cabin ? ` (${selectedRoute.cabin})` : ''}
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <select aria-label="Region pair" value={regionPair} onChange={(e) => setRegionPair(e.target.value)}>
            <option value="">All regions</option>
            {model.regionPairs.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>

          <button
            type="button"
            onClick={generatePostFromToggles}
            disabled={postLoading || toggledRows.length === 0}
          >
            {postLoading ? 'Generating…' : `Generate post (${toggledRows.length})`}
          </button>

          <details style={{ border: '1px solid #ddd', borderRadius: 6, padding: '6px 10px' }}>
            <summary style={{ cursor: 'pointer', userSelect: 'none' }}>Filters</summary>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center', marginTop: 10 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                Program
                <select value={program} onChange={(e) => setProgram(e.target.value)}>
                  <option value="">All</option>
                  {filterOptions.programs.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                Origin country
                <select value={originCountry} onChange={(e) => setOriginCountry(e.target.value)}>
                  <option value="">All</option>
                  {filterOptions.originCountries.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                Destination country
                <select value={destinationCountry} onChange={(e) => setDestinationCountry(e.target.value)}>
                  <option value="">All</option>
                  {filterOptions.destinationCountries.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                Origin airport
                <select value={originAirport} onChange={(e) => setOriginAirport(e.target.value)}>
                  <option value="">All</option>
                  {filterOptions.originAirports.map((a) => (
                    <option key={a} value={a}>
                      {a}
                    </option>
                  ))}
                </select>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                Destination airport
                <select value={destinationAirport} onChange={(e) => setDestinationAirport(e.target.value)}>
                  <option value="">All</option>
                  {filterOptions.destinationAirports.map((a) => (
                    <option key={a} value={a}>
                      {a}
                    </option>
                  ))}
                </select>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                Origin city
                <select value={origin} onChange={(e) => setOrigin(e.target.value)}>
                  <option value="">All</option>
                  {filterOptions.origins.map((o) => (
                    <option key={o} value={o}>
                      {o}
                    </option>
                  ))}
                </select>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                Destination city
                <select value={destination} onChange={(e) => setDestination(e.target.value)}>
                  <option value="">All</option>
                  {filterOptions.destinations.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                Cabin
                <select value={cabin} onChange={(e) => setCabin(e.target.value)}>
                  <option value="">All</option>
                  {filterOptions.cabins.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                Min total cost
                <input
                  value={minTotalCost}
                  onChange={(e) => setMinTotalCost(e.target.value)}
                  placeholder="0,00"
                  style={{ width: 90 }}
                />
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                Max total cost
                <input
                  value={maxTotalCost}
                  onChange={(e) => setMaxTotalCost(e.target.value)}
                  placeholder="9999,99"
                  style={{ width: 90 }}
                />
              </label>
            </div>
          </details>
        </div>
      )}

      {postError ? <pre style={{ background: '#fee', padding: 12, overflowX: 'auto' }}>{postError}</pre> : null}
      {postResult ? <pre style={{ background: '#f6f8fa', padding: 12, overflowX: 'auto' }}>{postResult}</pre> : null}

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={th} />
              <th style={th}>Region</th>
              <th style={th}>Origin</th>
              <th style={th}>Destination</th>
              <th style={th}>Cabin</th>
              <th style={th}>Outbound</th>
              {showReturn ? <th style={th}>Return</th> : null}
              <th style={th}>Mileage cost</th>
              <th style={th}>Taxes</th>
              <th style={th}>Total cost</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, idx) => (
              <tr
                key={idx}
                onClick={model.view === 'round' && !inDrilldown ? () => handleRoundRowClick(r) : undefined}
                style={
                  model.view === 'round' && !inDrilldown
                    ? { cursor: r.origin && r.destination ? 'pointer' : 'default' }
                    : undefined
                }
              >
                <td style={td} onClick={(e) => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={toggledRowIds.has(r.id)}
                    onChange={() => toggleRow(r.id)}
                  />
                </td>
                <td style={td}>{r.regionPair ?? ''}</td>
                <td style={td}>{r.origin ?? ''}</td>
                <td style={td}>{r.destination ?? ''}</td>
                <td style={td}>{r.cabin ?? ''}</td>
                <td style={td}>{r.outboundDates ?? ''}</td>
                {showReturn ? <td style={td}>{r.returnDates ?? ''}</td> : null}
                <td style={{ ...td, textAlign: 'right' }}>{r.mileageCost ?? ''}</td>
                <td style={{ ...td, textAlign: 'right' }}>{r.taxes ?? ''}</td>
                <td style={{ ...td, textAlign: 'right' }}>{r.totalCost ?? ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const th: React.CSSProperties = {
  textAlign: 'left',
  borderBottom: '1px solid #ddd',
  padding: '8px 10px',
  whiteSpace: 'nowrap'
};

const td: React.CSSProperties = {
  borderBottom: '1px solid #eee',
  padding: '8px 10px',
  verticalAlign: 'top',
  whiteSpace: 'nowrap'
};
