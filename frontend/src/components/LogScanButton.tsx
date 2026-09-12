import { useState } from 'react';
import { triggerLogScan, type LogScanResponse } from '../services/api';

interface LogScanButtonProps {
  onScanComplete: (result: LogScanResponse) => void;
}

function LogScanButton({ onScanComplete }: LogScanButtonProps) {
  const [root, setRoot] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    const trimmedRoot = root.trim();
    if (!trimmedRoot) {
      setError('Enter a log root path to scan.');
      return;
    }

    setIsScanning(true);
    setError(null);
    try {
      const result = await triggerLogScan(trimmedRoot);
      onScanComplete(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Log scan failed.');
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="log-scan-button">
      <input
        type="text"
        value={root}
        onChange={(event) => setRoot(event.target.value)}
        placeholder="Log root path"
      />
      <button type="button" onClick={handleScan} disabled={isScanning}>
        {isScanning ? 'Scanning…' : 'Scan Logs'}
      </button>
      {error && (
        <p className="scan-error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

export default LogScanButton;
