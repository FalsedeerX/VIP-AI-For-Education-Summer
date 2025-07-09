// src/lib/api.ts
export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

export async function postJson<T>(
  path: string,
  body: any,
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
  return res.json();
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
  return res.json();
}

export async function deleteJson<T>(
  path: string,
  body: any,
  includeCreds = false
): Promise<T> {
  const headers: Record<string,string> = {
    "Content-Type": "application/json",
  };

  const options: RequestInit = {
    method: "DELETE",
    headers,
    body: JSON.stringify(body),
  };

  if (includeCreds) {
    options.credentials = "include";
  }

  const res = await fetch(`${API_BASE}${path}`, options);

  if (!res.ok) {
    // try to see the actual validation errors:
    const text = await res.text();
    console.error("Delete failed:", text);
    throw new Error(text || res.statusText);
  }

  return res.json();
}

