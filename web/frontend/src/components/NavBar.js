// src/components/NavBar.js
import { Link } from 'react-router-dom';

export default function NavBar() {
  return (
    <nav className="bg-blue-900 text-white shadow">
      <div className="container mx-auto flex items-center p-4 space-x-6">
        <Link to="/" className="font-bold text-lg hover:text-orange-400">
          Results
        </Link>
        <Link to="/create" className="font-bold text-lg hover:text-orange-400">
          Create Player
        </Link>
      </div>
    </nav>
  );
}
