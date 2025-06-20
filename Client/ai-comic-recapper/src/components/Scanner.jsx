import { useEffect, useRef, useState } from 'react';
import Quagga from 'quagga';

const Scanner = ({ onDetected }) => {
  const videoRef = useRef(null);
  const [error, setError] = useState('');
  const [scanning, setScanning] = useState(true);
  const [lastCode, setLastCode] = useState('');

  useEffect(() => {
    if (!scanning) return;

    Quagga.init({
      inputStream: {
        name: "Live",
        type: "LiveStream",
        target: videoRef.current,
        constraints: {
          width: 640,
          height: 480,
          facingMode: "environment",
        },
      },
      locator: {
        patchSize: "medium",
        halfSample: true,
      },
      locate: true,
      numOfWorkers: navigator.hardwareConcurrency || 4,
      decoder: {
        readers: ["upc_reader"], // UPC-A barcodes
        debug: {
          drawBoundingBox: true,
          showFrequency: true,
          drawScanline: true,
          showPattern: true,
        },
      },
    }, (err) => {
      if (err) {
        console.error('Quagga init error:', err);
        setError('Error accessing webcam.');
        return;
      }
      Quagga.start();
    });

    const handleDetected = (result) => {
      const code = result?.codeResult?.code;
      if (code) {
        console.log("UPC-A Detected:", code);
        setLastCode(code);
        onDetected(code);
        setScanning(false);
      }
    };

    Quagga.onDetected(handleDetected);

    return () => {
      Quagga.offDetected(handleDetected);
      Quagga.stop();
    };
  }, [scanning, onDetected]);

  const handleRescan = () => {
    setLastCode('');
    setError('');
    setScanning(true);
  };

  if (error) return <p>{error}</p>;

  return (
    <div id="scanner-container">
      {scanning ? (
        <>
          <div
            ref={videoRef}
            style={{
              width: '640px',
              height: '480px',
              border: '2px solid #333',
              marginBottom: '10px',
            }}
          />
          <p>📷 Scanning for UPC-A barcode...</p>
        </>
      ) : (
        <>
          <h2>✅ Scanned Code:</h2>
          <p>{lastCode}</p>
          <button onClick={handleRescan}>🔄 Rescan</button>
        </>
      )}
    </div>
  );
};

export default Scanner;
