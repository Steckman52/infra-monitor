export interface ServiceSummary {
  id: number;
  name: string;
  ecosystem: string;
  repository_path: string;
  is_complete: boolean;
}

export interface ScanResponse {
  services_found: number;
  issues_found: number;
  unreachable_roots: string[];
}

async function parseJsonOrThrow<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function triggerScan(roots: string[]): Promise<ScanResponse> {
  const response = await fetch('/api/scan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ roots }),
  });
  return parseJsonOrThrow<ScanResponse>(response);
}

export async function listServices(): Promise<ServiceSummary[]> {
  const response = await fetch('/api/services');
  return parseJsonOrThrow<ServiceSummary[]>(response);
}
