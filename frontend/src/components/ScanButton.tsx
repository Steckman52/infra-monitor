import { useState } from 'react';
import { triggerScan, type ScanResponse } from '../services/api';

interface ScanButtonProps {
  onScanComplete: (result: ScanResponse) => void;
}

function ScanButton({ onScanComplete }: ScanButtonProps) {
  const [rootsInput, setRootsInput] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    const roots = rootsInput
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    if (roots.length === 0) {
      setError('Enter at least one repository root path to scan.');
      return;
    }

    setIsScanning(true);
    setError(null);
    try {
      const result = await triggerScan(roots);
      onScanComplete(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scan failed.');
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="scan-button">
      <textarea
        value={rootsInput}
        onChange={(event) => setRootsInput(event.target.value)}
        placeholder="One repository root path per line"
        rows={3}
      />
      <button type="button" onClick={handleScan} disabled={isScanning}>
        {isScanning ? 'Scanning…' : 'Scan'}
      </button>
      {error && (
        <p className="scan-error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

export default ScanButton;
