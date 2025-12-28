export type JsonValue =
  | null
  | boolean
  | number
  | string
  | JsonValue[]
  | { [key: string]: JsonValue };

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? '';

export async function fetchJson<T extends JsonValue>(
  path: string,
  params?: Record<string, string | number | boolean | (string | number)[] | undefined | null>
): Promise<T> {
  const url = new URL(API_BASE + path, window.location.origin);

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value === undefined || value === null) continue;
      if (Array.isArray(value)) {
        for (const v of value) url.searchParams.append(key, String(v));
      } else {
        url.searchParams.set(key, String(value));
      }
    }
  }

  const res = await fetch(url.toString(), { headers: { Accept: 'application/json' } });
  const text = await res.text();

  let json: unknown;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    throw new Error(`Non-JSON response (${res.status}): ${text.slice(0, 300)}`);
  }

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${JSON.stringify(json)}`);
  }

  return json as T;
}
