import { useEffect, useRef, useState } from 'react';
import Quagga from '@ericblade/quagga2';

export default function Scanner() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [message, setMessage] = useState('');
  const [isScanning, setIsScanning] = useState(true);

  useEffect(() => {
    if (!isScanning || !videoRef.current) return;

    Quagga.init({
      inputStream: {
        type: 'LiveStream',
        target: videoRef.current,
        constraints: {
          facingMode: 'environment',
        },
      },
      decoder: {
        readers: ['upc_reader'], // UPC-A only
      },
    }, (err) => {
      if (err) {
        console.error('Quagga init error:', err);
        return;
      }
      Quagga.start();
    });

    Quagga.onDetected(handleDetected);

    return () => {
      Quagga.stop();
      Quagga.offDetected(handleDetected);
    };
  }, [isScanning]);

  const handleDetected = async (result) => {
    const code = result.codeResult.code;
    if (code.length !== 12) return;

    setIsScanning(false); // Stop scanning

    try {
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      const video = videoRef.current.querySelector('video');

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('metadata', JSON.stringify({code}));
        formData.append('image', blob, 'frame.jpg');

        const response = await fetch('http://localhost:5000/recap', {
          method: 'POST',
          body: formData,
        });

        const data = await response.json();
        setMessage(data.message || 'Received response');
      }, 'image/jpeg');
    } catch (error) {
      console.error('Error sending data:', error);
      setMessage('Error sending data');
    }
  };

  const handleScanAgain = () => {
    setMessage('');
    setIsScanning(true);
  };

  return (
    <div className="p-4 space-y-4">
      {isScanning && (
        <div ref={videoRef} className="w-full max-w-md mx-auto border rounded" />
      )}
      <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>

      {!isScanning && (
        <div className="text-center space-y-4">
          <div className="font-semibold text-lg text-blue-700">{message}</div>
          <button
            onClick={handleScanAgain}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Scan Again
          </button>
        </div>
      )}
    </div>
  );
}
