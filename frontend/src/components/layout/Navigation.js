import React from 'react';
import { NavLink } from 'react-router-dom';

function Navigation() {
  return (
    <nav>
      <ul>
        <li><NavLink to="/" end><i className="fas fa-list"></i> Transactions</NavLink></li>
        <li><NavLink to="/import"><i className="fas fa-file-import"></i> Import Transactions</NavLink></li>
        <li><NavLink to="/import-patterns"><i className="fas fa-file-import"></i> Import Transaction Patterns</NavLink></li>
        <li><NavLink to="/review"><i className="fas fa-search"></i> Review Transactions</NavLink></li>
        <li><a href="http://localhost:8000/admin/" target="_blank" rel="noopener noreferrer"><i className="fas fa-cog"></i> Admin</a></li>
      </ul>
    </nav>
  );
}

export default Navigation;