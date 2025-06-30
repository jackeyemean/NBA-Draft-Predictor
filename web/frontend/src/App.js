// src/App.js
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import ResultsPage from './pages/ResultsPage';
import CreatePlayerPage from './pages/CreatePlayerPage';

export default function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <div className="container mx-auto p-4">
        <Routes>
          <Route path="/" element={<ResultsPage />} />
          <Route path="/create" element={<CreatePlayerPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
