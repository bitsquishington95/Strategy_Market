import React, { useEffect, useState } from 'react';
import { SuccessfulCEOsApp } from './components/SuccessfulCEOsApp';

function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [ceos, setCEOs] = useState([]);

  useEffect(() => {
    // Fetch CEOs from API
    fetch('/api/ceos')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch CEOs');
        }
        return response.json();
      })
      .then(data => {
        setCEOs(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching CEOs:', error);
        setError(error.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  return <SuccessfulCEOsApp initialData={ceos} />;
}

export default App;
