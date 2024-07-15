import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/layout/Header';
import Navigation from './components/layout/Navigation';
import TransactionList from './pages/transaction/TransactionList';
import TransactionImport from './pages/transaction/TransactionImport';
import TransactionPatternImport from './pages/transaction/TransactionPatternImport';
import TransactionReview from './pages/transaction/TransactionReview';
import './App.scss';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <Navigation />
        <Routes>
          <Route path="/" element={<TransactionList />} />
          <Route path="/import" element={<TransactionImport />} />
          <Route path="/import-patterns" element={<TransactionPatternImport />} />
          <Route path="/review" element={<TransactionReview />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;