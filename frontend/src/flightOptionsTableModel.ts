export type FlightOptionsTableRow = {
  id: string;
  kind: 'single_trip' | 'round_trip' | 'round_option';
  regionPair: string | null;

  originCountry: string | null;
  destinationCountry: string | null;
  originAirport: string | null;
  destinationAirport: string | null;
  program: string | null;

  origin: string | null;
  destination: string | null;
  cabin: string | null;
  outboundDates: string | null;
  returnDates: string | null;
  mileageCost: string | null;
  taxes: string | null;
  totalCost: string | null;
  totalCostCents: number | null;
  raw: unknown;
};

export type FlightOptionsTableModel = {
  view: 'single' | 'round';
  regionPairs: string[];
  rows: FlightOptionsTableRow[];
  // Always available to support drill-down from round-trip view.
  singleRows: FlightOptionsTableRow[];
};

function formatMoneyFromCents(cents: number): string {
  // Backend stores money as integer cents.
  // Brazilian formatting uses comma decimals.
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(cents / 100);
}

function formatMiles(value: number): string {
  return new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 }).format(value);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function pickTripId(trip: unknown): string | null {
  if (!isRecord(trip)) return null;
  // Common variants depending on how python objects were serialized.
  return (
    pickString(trip, 'availability_Id') ??
    pickString(trip, 'availabilityId') ??
    pickString(trip, 'AvailabilityID') ??
    pickString(trip, 'AvailabilityId') ??
    pickString(trip, 'ID')
  );
}

function buildRowId(kind: FlightOptionsTableRow['kind'], raw: unknown, fallback: Record<string, unknown>): string {
  if (kind === 'single_trip') {
    const tripId = pickTripId(raw);
    if (tripId) return `single:${tripId}`;
  }

  if (kind === 'round_trip') {
    if (isRecord(raw)) {
      const outId = pickString(raw, 'outbound_id') ?? pickString(raw, 'outboundId');
      const retId = pickString(raw, 'return_id') ?? pickString(raw, 'returnId');
      if (outId || retId) return `round:${outId ?? 'na'}:${retId ?? 'na'}`;

      const nestedOutbound = (raw as Record<string, unknown>)['outbound'];
      const nestedReturn = (raw as Record<string, unknown>)['return_'];
      const nestedOutId = pickTripId(nestedOutbound);
      const nestedRetId = pickTripId(nestedReturn);
      if (nestedOutId || nestedRetId) return `round:${nestedOutId ?? 'na'}:${nestedRetId ?? 'na'}`;
    }
  }

  if (kind === 'round_option' && isRecord(raw)) {
    const optionId = pickString(raw, 'ID') ?? pickString(raw, 'id');
    if (optionId) return `route:${optionId}`;
  }

  // Fallback: stable-ish fingerprint from core fields.
  const fp = [
    kind,
    fallback['regionPair'],
    fallback['origin'],
    fallback['destination'],
    fallback['cabin'],
    fallback['outboundDates'],
    fallback['returnDates']
  ]
    .map((v) => (typeof v === 'string' ? v : v === null || v === undefined ? '' : String(v)))
    .join('|');

  return `fp:${fp}`;
}

function pickDepartureDate(trip: unknown): string | null {
  if (!isRecord(trip)) return null;
  return pickString(trip, 'departure_date') ?? pickString(trip, 'departure');
}

function pickString(obj: Record<string, unknown>, key: string): string | null {
  const v = obj[key];
  return typeof v === 'string' && v.length ? v : null;
}

function pickNumber(obj: Record<string, unknown>, key: string): number | null {
  const v = obj[key];
  return typeof v === 'number' && Number.isFinite(v) ? v : null;
}

function pickNumberFromKeys(obj: Record<string, unknown>, keys: string[]): number | null {
  for (const k of keys) {
    const v = pickNumber(obj, k);
    if (v !== null) return v;
  }
  return null;
}

function getNested(obj: Record<string, unknown>, path: string[]): unknown {
  let current: unknown = obj;
  for (const key of path) {
    if (!isRecord(current)) return undefined;
    current = current[key];
  }
  return current;
}

function formatMaybeDateRange(from: unknown, to: unknown): string | null {
  if (typeof from === 'string' && typeof to === 'string') return `${from} → ${to}`;
  if (typeof from === 'string') return from;
  return null;
}

function extractRegionPair(raw: unknown): string | null {
  if (!isRecord(raw)) return null;

  // Common shapes:
  // - { region: "Africa-Europe" }
  // - { origin_region: "Africa", destination_region: "Europe" }
  // - { outbound: { region: "Africa" }, return_: { region: "Europe" } }
  const directRegion = pickString(raw, 'region');
  if (directRegion && directRegion.includes('-')) return directRegion;

  const originRegion = pickString(raw, 'origin_region');
  const destinationRegion = pickString(raw, 'destination_region');
  if (originRegion && destinationRegion) return `${originRegion}-${destinationRegion}`;

  const outboundRegion = isRecord(raw.outbound as unknown) ? pickString(raw.outbound as Record<string, unknown>, 'region') : null;
  const returnRegion = isRecord((raw as Record<string, unknown>)['return_'])
    ? pickString((raw as Record<string, unknown>)['return_'] as Record<string, unknown>, 'region')
    : null;
  if (outboundRegion && returnRegion) return `${outboundRegion}-${returnRegion}`;

  return directRegion; // fallback (single region)
}

function buildSinglesIndex(singleTrips: unknown[]) {
  const byId = new Map<string, unknown>();
  for (const t of singleTrips) {
    const id = pickTripId(t);
    if (id) byId.set(id, t);
  }
  return byId;
}

function resolveRoundTripSides(
  rawRoundTrip: unknown,
  singlesById: Map<string, unknown>
): { outbound: unknown | null; return_: unknown | null } {
  if (!isRecord(rawRoundTrip)) return { outbound: null, return_: null };

  // Shape A: nested objects are present.
  const nestedOutbound = (rawRoundTrip as Record<string, unknown>)['outbound'];
  const nestedReturn = (rawRoundTrip as Record<string, unknown>)['return_'];
  if (nestedOutbound || nestedReturn) {
    return { outbound: nestedOutbound ?? null, return_: nestedReturn ?? null };
  }

  // Shape B: relational IDs only (Google Sheets style): outbound_id / return_id
  const outboundId = pickString(rawRoundTrip, 'outbound_id') ?? pickString(rawRoundTrip, 'outboundId');
  const returnId = pickString(rawRoundTrip, 'return_id') ?? pickString(rawRoundTrip, 'returnId');

  const outbound = outboundId ? singlesById.get(outboundId) ?? null : null;
  const return_ = returnId ? singlesById.get(returnId) ?? null : null;

  return { outbound, return_ };
}

function extractCoreFields(
  kind: FlightOptionsTableRow['kind'],
  raw: unknown
): Omit<FlightOptionsTableRow, 'id' | 'kind' | 'raw' | 'regionPair'> {
  if (!isRecord(raw)) {
    return {
      originCountry: null,
      destinationCountry: null,
      originAirport: null,
      destinationAirport: null,
      program: null,
      origin: null,
      destination: null,
      cabin: null,
      outboundDates: null,
      returnDates: null,
      mileageCost: null,
      taxes: null,
      totalCost: null,
      totalCostCents: null
    };
  }

  if (kind === 'single_trip') {
    const origin = pickString(raw, 'origin_city') ?? pickString(raw, 'origin_airport');
    const destination = pickString(raw, 'destination_city') ?? pickString(raw, 'destination_airport');
    const originCountry = pickString(raw, 'origin_country');
    const destinationCountry = pickString(raw, 'destination_country');
    const originAirport = pickString(raw, 'origin_airport');
    const destinationAirport = pickString(raw, 'destination_airport');
    const program = pickString(raw, 'source') ?? pickString(raw, 'program') ?? pickString(raw, 'provider');
    const cabin = pickString(raw, 'cabin');
    // Show boarding date only (departure), not arrival and not release date.
    const outboundDates = pickString(raw, 'departure_date');
    const returnDates = null;

    const mileageCostValue = pickNumberFromKeys(raw, ['mileage_cost', 'mileageCost', 'mileageCostValue']);
    const mileageCost = mileageCostValue !== null ? formatMiles(mileageCostValue) : null;

    const taxesCents =
      pickNumberFromKeys(raw, ['normal_taxes', 'normalTaxes']) ??
      pickNumberFromKeys(raw, ['taxes', 'taxesValue']);
    const taxes = taxesCents !== null ? formatMoneyFromCents(taxesCents) : null;

    const totalCostCents =
      pickNumberFromKeys(raw, ['normal_total_cost', 'normalTotalCost']) ??
      pickNumberFromKeys(raw, ['total_cost', 'totalCost']);
    const totalCost = totalCostCents !== null ? formatMoneyFromCents(totalCostCents) : null;

    return {
      originCountry,
      destinationCountry,
      originAirport,
      destinationAirport,
      program,
      origin,
      destination,
      cabin,
      outboundDates,
      returnDates,
      mileageCost,
      taxes,
      totalCost,
      totalCostCents: totalCostCents ?? null
    };
  }

  if (kind === 'round_trip') {
    // NOTE: For round trips we intentionally keep extraction minimal here.
    // The join/enrichment (Google Sheets-like) is done in the builder where we
    // have access to single_trips for lookups.
    const totalCostCents =
      pickNumberFromKeys(raw, ['normal_total_cost', 'normalTotalCost']) ??
      pickNumberFromKeys(raw, ['total_cost', 'totalCost']);
    const totalCost = totalCostCents !== null ? formatMoneyFromCents(totalCostCents) : null;
    return {
      originCountry: null,
      destinationCountry: null,
      originAirport: null,
      destinationAirport: null,
      program: null,
      origin: null,
      destination: null,
      cabin: null,
      outboundDates: null,
      returnDates: null,
      mileageCost: null,
      taxes: null,
      totalCost,
      totalCostCents: totalCostCents ?? null
    };
  }

  // round_option
  const origin = pickString(raw, 'origin_city');
  const destination = pickString(raw, 'destination_city');
  const originCountry = pickString(raw, 'origin_country');
  const destinationCountry = pickString(raw, 'destination_country');
  const originAirport = pickString(raw, 'origin_airport') ?? pickString(raw, 'originAirport');
  const destinationAirport = pickString(raw, 'destination_airport') ?? pickString(raw, 'destinationAirport');
  const program = pickString(raw, 'source') ?? pickString(raw, 'program') ?? pickString(raw, 'provider');
  const cabin = pickString(raw, 'cabin');

  const departureDates = raw.departure_dates;
  const returnDates = raw.return_dates;
  const firstOut = Array.isArray(departureDates) && typeof departureDates[0] === 'string' ? departureDates[0] : null;
  const firstRet = Array.isArray(returnDates) && typeof returnDates[0] === 'string' ? returnDates[0] : null;

  // Show boarding dates only (no ranges).
  const outboundDates = firstOut;
  const returnDatesFormatted = firstRet;

  // Route summary rows: user wants the *highest* values (not averages).
  const highMileage = pickNumberFromKeys(raw, ['highest_mileage_cost', 'highestMileageCost']);
  const avgMileage = pickNumberFromKeys(raw, ['average_mileage_cost', 'averageMileageCost']);
  const lowMileage = pickNumberFromKeys(raw, ['lowest_mileage_cost', 'lowestMileageCost']);
  const mileageCostValue = highMileage ?? avgMileage ?? lowMileage;
  const mileageCost = mileageCostValue !== null ? formatMiles(mileageCostValue) : null;

  const highTaxes = pickNumberFromKeys(raw, ['highest_taxes', 'highestTaxes']);
  const avgTaxes = pickNumberFromKeys(raw, ['average_taxes', 'averageTaxes']);
  const lowTaxes = pickNumberFromKeys(raw, ['lowest_taxes', 'lowestTaxes']);
  const taxesValue = highTaxes ?? avgTaxes ?? lowTaxes;
  const taxes = taxesValue !== null ? formatMoneyFromCents(taxesValue) : null;

  const highTotal = pickNumberFromKeys(raw, ['highest_total_cost', 'highestTotalCost']);
  const avgTotal = pickNumberFromKeys(raw, ['average_total_cost', 'averageTotalCost']);
  const lowTotal = pickNumberFromKeys(raw, ['lowest_total_cost', 'lowestTotalCost']);
  const totalCostCents = highTotal ?? avgTotal ?? lowTotal ?? null;
  const totalCost = totalCostCents !== null ? formatMoneyFromCents(totalCostCents) : null;

  return {
    originCountry,
    destinationCountry,
    originAirport,
    destinationAirport,
    program,
    origin,
    destination,
    cabin,
    outboundDates,
    returnDates: returnDatesFormatted,
    mileageCost,
    taxes,
    totalCost,
    totalCostCents
  };
}

export function buildFlightOptionsTableModel(input: unknown): FlightOptionsTableModel {
  // API returns:
  // - { status: 200, data: FlightOptions }
  // Some callers/tools may wrap this further, so unwrap defensively until
  // we either hit the FlightOptions shape or run out of `data` envelopes.
  let root: unknown = input;
  while (
    isRecord(root) &&
    'data' in root &&
    !('single_trips' in root || 'round_trips' in root || 'round_options' in root)
  ) {
    root = (root as Record<string, unknown>)['data'];
  }

  if (!isRecord(root)) return { view: 'single', rows: [], regionPairs: [], singleRows: [] };

  const singleTrips = asArray(root['single_trips']);
  const roundTrips = asArray(root['round_trips']);
  const roundOptions = asArray(root['round_options']);

  const singlesById = buildSinglesIndex(singleTrips);

  const singleRows: FlightOptionsTableRow[] = [];
  for (const item of singleTrips) {
    const regionPair = extractRegionPair(item);
    const core = extractCoreFields('single_trip', item);
    const id = buildRowId('single_trip', item, { regionPair, ...core });
    singleRows.push({ id, kind: 'single_trip', regionPair, ...core, raw: item });
  }

  const rows: FlightOptionsTableRow[] = [];

  const view: FlightOptionsTableModel['view'] =
    roundTrips.length > 0 || roundOptions.length > 0 ? 'round' : 'single';

  if (view === 'single') {
    // Oneway: show singles.
    rows.push(...singleRows);
  } else {
    // Roundtrip view:
    // - singles_rounds_relational => roundTrips (relational rows)
    // - rounds => roundOptions (route summaries)
    if (roundOptions.length > 0) {
      for (const item of roundOptions) {
        const regionPair = extractRegionPair(item);
        const core = extractCoreFields('round_option', item);
        const id = buildRowId('round_option', item, { regionPair, ...core });
        rows.push({ id, kind: 'round_option', regionPair, ...core, raw: item });
      }
    } else {
      // Fallback: if backend didn't provide summaries, render relational round trips.
      for (const item of roundTrips) {
        const regionPair = extractRegionPair(item);

        const { outbound, return_ } = resolveRoundTripSides(item, singlesById);
        const originCountry = isRecord(outbound) ? pickString(outbound, 'origin_country') : null;
        const destinationCountry = isRecord(outbound) ? pickString(outbound, 'destination_country') : null;
        const originAirport = isRecord(outbound) ? pickString(outbound, 'origin_airport') : null;
        const destinationAirport = isRecord(outbound) ? pickString(outbound, 'destination_airport') : null;
        const program =
          (isRecord(outbound) ? pickString(outbound, 'source') ?? pickString(outbound, 'program') ?? pickString(outbound, 'provider') : null) ??
          (isRecord(item) ? pickString(item, 'source') ?? pickString(item, 'program') ?? pickString(item, 'provider') : null);
        const origin = isRecord(outbound)
          ? (pickString(outbound, 'origin_city') ?? pickString(outbound, 'origin_airport'))
          : null;
        const destination = isRecord(outbound)
          ? (pickString(outbound, 'destination_city') ?? pickString(outbound, 'destination_airport'))
          : null;
        const cabin = isRecord(outbound) ? pickString(outbound, 'cabin') : null;
        const outboundDates = pickDepartureDate(outbound);
        const returnDates = pickDepartureDate(return_);

        const base = extractCoreFields('round_trip', item);

        const outMiles = isRecord(outbound)
          ? pickNumberFromKeys(outbound, ['mileage_cost', 'mileageCost', 'mileageCostValue'])
          : null;
        const retMiles = isRecord(return_)
          ? pickNumberFromKeys(return_, ['mileage_cost', 'mileageCost', 'mileageCostValue'])
          : null;
        const mileageCostValue =
          outMiles !== null && retMiles !== null
            ? outMiles + retMiles
            : outMiles !== null
              ? outMiles
              : retMiles;

        const outTaxes = isRecord(outbound)
          ? (pickNumberFromKeys(outbound, ['normal_taxes', 'normalTaxes']) ?? pickNumberFromKeys(outbound, ['taxes', 'taxesValue']))
          : null;
        const retTaxes = isRecord(return_)
          ? (pickNumberFromKeys(return_, ['normal_taxes', 'normalTaxes']) ?? pickNumberFromKeys(return_, ['taxes', 'taxesValue']))
          : null;
        const taxesCents =
          outTaxes !== null && retTaxes !== null
            ? outTaxes + retTaxes
            : outTaxes !== null
              ? outTaxes
              : retTaxes;

        const outTotal = isRecord(outbound)
          ? (pickNumberFromKeys(outbound, ['normal_total_cost', 'normalTotalCost']) ?? pickNumberFromKeys(outbound, ['total_cost', 'totalCost']))
          : null;
        const retTotal = isRecord(return_)
          ? (pickNumberFromKeys(return_, ['normal_total_cost', 'normalTotalCost']) ?? pickNumberFromKeys(return_, ['total_cost', 'totalCost']))
          : null;
        const derivedTotalCents =
          outTotal !== null && retTotal !== null
            ? outTotal + retTotal
            : outTotal !== null
              ? outTotal
              : retTotal;

        const rowCore = {
          originCountry,
          destinationCountry,
          originAirport,
          destinationAirport,
          program,
          origin,
          destination,
          cabin,
          outboundDates,
          returnDates,
          mileageCost: mileageCostValue !== null ? formatMiles(mileageCostValue) : null,
          taxes: taxesCents !== null ? formatMoneyFromCents(taxesCents) : null,
          totalCost: base.totalCost ?? (derivedTotalCents !== null ? formatMoneyFromCents(derivedTotalCents) : null),
          totalCostCents: base.totalCostCents ?? (derivedTotalCents ?? null)
        };
        const id = buildRowId('round_trip', item, { regionPair, ...rowCore });
        rows.push({ id, kind: 'round_trip', regionPair, ...rowCore, raw: item });
      }
    }
  }

  const regionPairs = Array.from(
    new Set(
      rows
        .map((r) => r.regionPair)
        .filter((v): v is string => typeof v === 'string' && v.length > 0)
    )
  ).sort((a, b) => a.localeCompare(b));

  return { view, rows, regionPairs, singleRows };
}
