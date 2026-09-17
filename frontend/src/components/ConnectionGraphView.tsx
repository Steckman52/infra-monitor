import { Network } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import type { NodeConnections } from '../services/api';

interface ConnectionGraphViewProps {
  nodes: NodeConnections[];
}

function ConnectionGraphView({ nodes }: ConnectionGraphViewProps) {
  const { t } = useLanguage();

  if (nodes.length === 0) {
    return <p className="empty-state">{t.connections.empty}</p>;
  }

  const basisLabel = (basis: string) =>
    basis === 'shared_network' ? t.connections.sharedNetwork : basis === 'depends_on' ? t.connections.dependsOn : t.connections.both;

  // Two unrelated repositories can declare a compose service with the same
  // generic name (e.g. "db"); without the repository path they'd render as
  // if they were the same external node.
  const nodeLabel = (node: NodeConnections['node']) =>
    node.type === 'external' && node.repository_path
      ? `${node.name} (${t.serviceDetail.external} — ${node.repository_path})`
      : node.type === 'external'
        ? `${node.name} (${t.serviceDetail.external})`
        : node.name;

  return (
    <>
      {nodes.map((entry) => (
        <div key={`${entry.node.type}:${entry.node.id}`} className="activity-row" style={{ cursor: 'default' }}>
          <div className="activity-icon">
            <Network />
          </div>
          <div>
            <div className="activity-title">
              <b>{nodeLabel(entry.node)}</b>
            </div>
            {entry.connections.map((edge, index) => (
              <div key={index} className="activity-meta">
                → {nodeLabel(edge.node)} — {basisLabel(edge.relationship_basis)}
              </div>
            ))}
          </div>
        </div>
      ))}
    </>
  );
}

export default ConnectionGraphView;
