// src/lib/api.ts
export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

export async function postJson<T>(
  path: string,
  body: unknown,
  includeCreds = false
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    ...(includeCreds && { credentials: "include" }),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(errText || res.statusText);
  }
  const data = await res.json();
  return data as T;
}

export async function getJson<T>(
  path: string,
  includeCreds = false
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    ...(includeCreds && { credentials: "include" }),
  });
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(errText || res.statusText);
  }
  const data = await res.json();
  return data as T;
}

export async function deleteJson<T>(
  path: string,
  body: unknown,
  includeCreds = false
): Promise<T> {
  const options: RequestInit = {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };

  if (includeCreds) {
    options.credentials = "include";
  }

  const res = await fetch(`${API_BASE}${path}`, options);

  if (!res.ok) {
    const text = await res.text();
    console.error("Delete failed:", text);
    throw new Error(text || res.statusText);
  }

  const data = await res.json();
  return data as T;
}
