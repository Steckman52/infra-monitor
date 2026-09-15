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
  adrs_found: number;
}

export interface AdrSummary {
  id: number;
  title: string;
  normalized_status: string;
  raw_status: string | null;
  date: string | null;
  source_path: string;
  has_secret_warning: boolean;
}

export interface RelatedAdr {
  adr_id: number;
  title: string;
}

export interface RelatedService {
  service_id: number;
  service_name: string;
}

export interface AdrDetail extends AdrSummary {
  content: string;
  supersedes: RelatedAdr[];
  superseded_by: RelatedAdr[];
  amends: RelatedAdr[];
  amended_by: RelatedAdr[];
  related_services: RelatedService[];
}

export interface AdrIssue {
  type: 'parse_failure' | 'secret_warning';
  path: string;
  reason: string;
  adr_id: number | null;
}

export interface Dependency {
  name: string;
  declared_version: string | null;
}

export interface ConflictingService {
  service_id: number;
  service_name: string;
  declared_version: string | null;
}

export interface CompatibilityRisk {
  name: string;
  ecosystem: string;
  declared_version: string | null;
  conflicting_with: ConflictingService[];
}

export interface ServiceDetail extends ServiceSummary {
  manifest_path: string;
  last_scanned_at: string;
  dependencies: Dependency[];
  compatibility_risks: CompatibilityRisk[];
  connections: ConnectionEdge[];
  related_adrs: RelatedAdr[];
  recent_error_groups: ErrorGroupSummary[];
}

export interface ScanIssue {
  id: number;
  manifest_path: string;
  repository_path: string;
  issue_type: 'unparsable' | 'incomplete_data' | 'unreachable_path';
  reason: string;
  service_id: number | null;
  detected_at: string;
}

export interface LogScanIssue {
  id: number;
  path: string;
  issue_type: 'unattributed' | 'unreadable';
  reason: string;
  detected_at: string;
}

export interface CompatibilityEntry {
  service_id: number;
  service_name: string;
  declared_version: string | null;
  major_version: number | null;
}

export interface CompatibilityGroup {
  name: string;
  ecosystem: string;
  status: 'compatible' | 'compatibility_risk';
  has_not_comparable: boolean;
  entries: CompatibilityEntry[];
}

export interface NodeRef {
  type: 'service' | 'external';
  id: number;
  name: string;
}

export interface ConnectionEdge {
  node: NodeRef;
  relationship_basis: 'shared_network' | 'depends_on' | 'both';
}

export interface NodeConnections {
  node: NodeRef;
  connections: ConnectionEdge[];
}

export interface LogScanResponse {
  error_groups_found: number;
  issues_found: number;
  root_unreachable: boolean;
}

export interface ErrorGroupSummary {
  id: number;
  service_id: number | null;
  service_name: string | null;
  unattributed_source_path: string | null;
  normalized_template: string;
  severity_marker: string;
  occurrence_count: number;
  first_seen: string | null;
  last_seen: string | null;
}

export interface ErrorOccurrence {
  raw_text: string;
  occurred_at: string | null;
  source_log_path: string;
  line_number: number;
}

export interface ErrorGroupDetail extends ErrorGroupSummary {
  example_text: string;
  occurrences: ErrorOccurrence[];
}

export interface DashboardSummary {
  services_count: number;
  scan_issues_count: number;
  compatibility_risks_count: number;
  error_groups_count: number;
  log_scan_issues_count: number;
  adrs_count: number;
  adr_issues_count: number;
  last_registry_scan_at: string | null;
  last_log_scan_at: string | null;
}

async function parseJsonOrThrow<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail: string | undefined;
    try {
      const body = await response.json();
      if (body && typeof body.detail === 'string') {
        detail = body.detail;
      }
    } catch {
      // Response body wasn't JSON (or was empty) -- fall through to the generic message.
    }
    throw new Error(detail ?? `Request failed with status ${response.status}`);
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

export async function getServiceDetail(id: number): Promise<ServiceDetail> {
  const response = await fetch(`/api/services/${id}`);
  return parseJsonOrThrow<ServiceDetail>(response);
}

export async function listScanIssues(): Promise<ScanIssue[]> {
  const response = await fetch('/api/scan-issues');
  return parseJsonOrThrow<ScanIssue[]>(response);
}

export async function listCompatibility(): Promise<CompatibilityGroup[]> {
  const response = await fetch('/api/dependency-compatibility');
  return parseJsonOrThrow<CompatibilityGroup[]>(response);
}

export async function listConnections(): Promise<NodeConnections[]> {
  const response = await fetch('/api/connections');
  return parseJsonOrThrow<NodeConnections[]>(response);
}

export async function triggerLogScan(root: string): Promise<LogScanResponse> {
  const response = await fetch('/api/log-scan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ root }),
  });
  return parseJsonOrThrow<LogScanResponse>(response);
}

export async function listErrorGroups(): Promise<ErrorGroupSummary[]> {
  const response = await fetch('/api/error-groups');
  return parseJsonOrThrow<ErrorGroupSummary[]>(response);
}

export async function getErrorGroupDetail(id: number): Promise<ErrorGroupDetail> {
  const response = await fetch(`/api/error-groups/${id}`);
  return parseJsonOrThrow<ErrorGroupDetail>(response);
}

export async function listLogScanIssues(): Promise<LogScanIssue[]> {
  const response = await fetch('/api/log-scan-issues');
  return parseJsonOrThrow<LogScanIssue[]>(response);
}

export async function listAdrs(): Promise<AdrSummary[]> {
  const response = await fetch('/api/adrs');
  return parseJsonOrThrow<AdrSummary[]>(response);
}

export async function getAdrDetail(id: number): Promise<AdrDetail> {
  const response = await fetch(`/api/adrs/${id}`);
  return parseJsonOrThrow<AdrDetail>(response);
}

export async function listAdrIssues(): Promise<AdrIssue[]> {
  const response = await fetch('/api/adr-issues');
  return parseJsonOrThrow<AdrIssue[]>(response);
}

export async function getDashboard(): Promise<DashboardSummary> {
  const response = await fetch('/api/dashboard');
  return parseJsonOrThrow<DashboardSummary>(response);
}

export interface PickDirectoryResponse {
  path: string | null;
}

export async function pickDirectory(): Promise<PickDirectoryResponse> {
  const response = await fetch('/api/pick-directory');
  return parseJsonOrThrow<PickDirectoryResponse>(response);
}
