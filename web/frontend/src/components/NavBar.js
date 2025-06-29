import { Link } from 'react-router-dom';

export default function NavBar() {
  return (
    <nav className="bg-gray-800 text-white p-4">
      <ul className="flex space-x-4">
        <li><Link to="/">Results</Link></li>
        <li><Link to="/create">Create Player</Link></li>
      </ul>
    </nav>
  );
}
