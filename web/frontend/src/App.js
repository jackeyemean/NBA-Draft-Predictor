import React from 'react';
import ResultsPage from './pages/ResultsPage';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-blue-900 text-white py-4 shadow">
        <div className="container mx-auto text-center">
          <h1 className="text-3xl font-bold">NBA Draft Predictor</h1>
        </div>
      </header>
      <main className="container mx-auto p-4">
        <ResultsPage />
      </main>
    </div>
  );
}
