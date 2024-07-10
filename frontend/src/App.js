import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/Header';
import Navigation from './components/Navigation';
import TransactionList from './components/Transaction/TransactionList';
import TransactionImport from './components/Transaction/TransactionImport';
import TransactionPatternImport from './components/Transaction/TransactionPatternImport';
import TransactionReview from './components/Transaction/TransactionReview';
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