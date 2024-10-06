import React, { useEffect, useState } from 'react';
import './App.css';
import catalog from './catalog.json'

function App() {
  const [catalog, setCatalog] = useState([]);

  useEffect(() => {
    fetch('./catalog.json')
      .then(response => response.json())
      .then(data => setCatalog(data))
      .catch(error => console.error('Error loading JSON:', error));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Catalog</h1>
        <ul>
          {catalog.map(item => (
            <li key={item.subj}>
              <h2>{item.crse}</h2>
              <p>{item.desc}</p>
              <p>Price: ${item.price.toFixed(2)}</p>
            </li>
          ))}
        </ul>
      </header>
    </div>
  );
}

export default App;
