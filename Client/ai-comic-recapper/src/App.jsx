import { useState } from 'react'
import './App.css'
import Scanner from './components/Scanner'

function App() {
  const [scannedCode, setScannedCode] = useState('');

  return (
    <div>
      <h1>AI Comic Book Recapper</h1>

      <Scanner onDetected={setScannedCode} />
      </div>
  );
};

export default App
