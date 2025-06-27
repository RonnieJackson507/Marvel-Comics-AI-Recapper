import { useState } from 'react'
import './App.css'
import Scanner from './components/Scanner'
import Footer from './components/Footer';
import Header from './components/Header';

function App() {
  const [scannedCode, setScannedCode] = useState('');

  return (
    <div>
      <Header/>

      <Scanner />

      <Footer/>
      </div>
  );
};

export default App
