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

  return (
    <>
      {nodes.map((entry) => (
        <div key={`${entry.node.type}:${entry.node.id}`} className="activity-row" style={{ cursor: 'default' }}>
          <div className="activity-icon">
            <Network />
          </div>
          <div>
            <div className="activity-title">
              <b>{entry.node.name}</b>
              {entry.node.type === 'external' && ` (${t.serviceDetail.external})`}
            </div>
            {entry.connections.map((edge, index) => (
              <div key={index} className="activity-meta">
                → {edge.node.name}
                {edge.node.type === 'external' && ` (${t.serviceDetail.external})`} — {basisLabel(edge.relationship_basis)}
              </div>
            ))}
          </div>
        </div>
      ))}
    </>
  );
}

export default ConnectionGraphView;
