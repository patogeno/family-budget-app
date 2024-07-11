import React, { useState, useEffect, useCallback } from 'react';
import { getTransactions, getTransactionTypes, getBudgetGroups, getAccountNames } from '../../services/api';

function TransactionList() {
  const [transactions, setTransactions] = useState([]);
  const [filteredTransactions, setFilteredTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [transactionTypes, setTransactionTypes] = useState([]);
  const [budgetGroups, setBudgetGroups] = useState([]);
  const [accountNames, setAccountNames] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [transactionsPerPage, setTransactionsPerPage] = useState(10);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'ascending' });

  // Add state for filters
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    description: '',
    type: '',
    budget: '',
    account: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [transactionsResponse, typesResponse, groupsResponse, accountsResponse] = await Promise.all([
        getTransactions(),
        getTransactionTypes(),
        getBudgetGroups(),
        getAccountNames()
      ]);
      setTransactions(transactionsResponse.data);
      setTransactionTypes(typesResponse.data);
      setBudgetGroups(groupsResponse.data);
      setAccountNames(accountsResponse.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch data');
      setLoading(false);
    }
  };

  const applyFilters = useCallback(() => {
    let filtered = transactions;

    if (filters.dateFrom) {
      filtered = filtered.filter(t => new Date(t.date) >= new Date(filters.dateFrom));
    }
    if (filters.dateTo) {
      filtered = filtered.filter(t => new Date(t.date) <= new Date(filters.dateTo));
    }
    if (filters.description) {
      filtered = filtered.filter(t => 
        t.description.toLowerCase().includes(filters.description.toLowerCase())
      );
    }
    if (filters.type) {
      filtered = filtered.filter(t => 
        t.transaction_type && t.transaction_type.toString() === filters.type
      );
    }
    if (filters.budget) {
      filtered = filtered.filter(t => 
        t.budget_group && t.budget_group.toString() === filters.budget
      );
    }
    if (filters.account) {
      filtered = filtered.filter(t => 
        t.account_name && t.account_name.toString() === filters.account
      );
    }

    setFilteredTransactions(filtered);
  }, [transactions, filters]);

  useEffect(() => {
    applyFilters();
  }, [applyFilters]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const clearAllFilters = () => {
    setFilters({
      dateFrom: '',
      dateTo: '',
      description: '',
      type: '',
      budget: '',
      account: ''
    });
  };

  const getAmountClass = (amount) => {
    const numericAmount = parseFloat(amount);
    if (numericAmount > 0) {
      return 'amount-positive';
    } else if (numericAmount < -500) {
      return 'amount-negative-high';
    } else if (numericAmount < -150) {
      return 'amount-negative-medium';
    }
    return '';
  };

  const sortTransactions = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });

    const sortedTransactions = [...filteredTransactions].sort((a, b) => {
      if (a[key] < b[key]) return direction === 'ascending' ? -1 : 1;
      if (a[key] > b[key]) return direction === 'ascending' ? 1 : -1;
      return 0;
    });

    setFilteredTransactions(sortedTransactions);
  };

  // Pagination
  const indexOfLastTransaction = currentPage * transactionsPerPage;
  const indexOfFirstTransaction = indexOfLastTransaction - transactionsPerPage;
  const currentTransactions = filteredTransactions.slice(indexOfFirstTransaction, indexOfLastTransaction);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  const renderPaginationButtons = () => {
    const totalPages = Math.ceil(filteredTransactions.length / transactionsPerPage);
    let buttons = [];

    if (totalPages <= 10) {
      for (let i = 1; i <= totalPages; i++) {
        buttons.push(
          <button key={i} onClick={() => paginate(i)} className={currentPage === i ? 'active' : ''}>
            {i}
          </button>
        );
      }
    } else {
      // Always show first page
      buttons.push(
        <button key={1} onClick={() => paginate(1)} className={currentPage === 1 ? 'active' : ''}>
          1
        </button>
      );

      if (currentPage > 4) {
        buttons.push(<span key="ellipsis1">...</span>);
      }

      // Show pages around current page
      for (let i = Math.max(2, currentPage - 2); i <= Math.min(totalPages - 1, currentPage + 2); i++) {
        buttons.push(
          <button key={i} onClick={() => paginate(i)} className={currentPage === i ? 'active' : ''}>
            {i}
          </button>
        );
      }

      if (currentPage < totalPages - 3) {
        buttons.push(<span key="ellipsis2">...</span>);
      }

      // Always show last page
      buttons.push(
        <button key={totalPages} onClick={() => paginate(totalPages)} className={currentPage === totalPages ? 'active' : ''}>
          {totalPages}
        </button>
      );
    }

    return buttons;
  };

  const handleTransactionsPerPageChange = (e) => {
    setTransactionsPerPage(Number(e.target.value));
    setCurrentPage(1); // Reset to first page when changing items per page
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="transaction-list">
      <h2>Transactions</h2>
      <div className="filters">
        <input
          type="date"
          name="dateFrom"
          value={filters.dateFrom}
          onChange={handleFilterChange}
        />
        <input
          type="date"
          name="dateTo"
          value={filters.dateTo}
          onChange={handleFilterChange}
        />
        <input
          type="text"
          name="description"
          placeholder="Filter by description"
          value={filters.description}
          onChange={handleFilterChange}
        />
        <select
          name="type"
          value={filters.type}
          onChange={handleFilterChange}
        >
          <option value="">All Types</option>
          {transactionTypes.map(type => (
            <option key={type.id} value={type.id}>{type.name}</option>
          ))}
        </select>
        <select
          name="budget"
          value={filters.budget}
          onChange={handleFilterChange}
        >
          <option value="">All Budgets</option>
          {budgetGroups.map(group => (
            <option key={group.id} value={group.id}>{group.name}</option>
          ))}
        </select>
        <select
          name="account"
          value={filters.account}
          onChange={handleFilterChange}
        >
          <option value="">All Accounts</option>
          {accountNames.map(account => (
            <option key={account.id} value={account.id}>{account.name}</option>
          ))}
        </select>
        <button onClick={clearAllFilters} className="clear-filters-btn">Clear All Filters</button>
        <select
          value={transactionsPerPage}
          onChange={handleTransactionsPerPageChange}
          className="transactions-per-page"
        >
          <option value={10}>10 per page</option>
          <option value={25}>25 per page</option>
          <option value={50}>50 per page</option>
          <option value={100}>100 per page</option>
        </select>
      </div>
      <table>
        <thead>
          <tr>
            <th onClick={() => sortTransactions('date')}>Date {sortConfig.key === 'date' && (sortConfig.direction === 'ascending' ? '▲' : '▼')}</th>
            <th onClick={() => sortTransactions('description')}>Description {sortConfig.key === 'description' && (sortConfig.direction === 'ascending' ? '▲' : '▼')}</th>
            <th onClick={() => sortTransactions('amount')}>Amount {sortConfig.key === 'amount' && (sortConfig.direction === 'ascending' ? '▲' : '▼')}</th>
            <th onClick={() => sortTransactions('account_name')}>Account {sortConfig.key === 'account_name' && (sortConfig.direction === 'ascending' ? '▲' : '▼')}</th>
            <th onClick={() => sortTransactions('budget_group')}>Budget Group {sortConfig.key === 'budget_group' && (sortConfig.direction === 'ascending' ? '▲' : '▼')}</th>
            <th onClick={() => sortTransactions('transaction_type')}>Transaction Type {sortConfig.key === 'transaction_type' && (sortConfig.direction === 'ascending' ? '▲' : '▼')}</th>
          </tr>
        </thead>
        <tbody>
          {currentTransactions.map((transaction) => (
            <tr key={transaction.id}>
              <td>{transaction.date}</td>
              <td>{transaction.description}</td>
              <td className={getAmountClass(transaction.amount)}>{transaction.amount}</td>
              <td>{accountNames.find(a => a.id === transaction.account_name)?.name || 'Unknown'}</td>
              <td>{budgetGroups.find(b => b.id === transaction.budget_group)?.name || 'Unassigned'}</td>
              <td>{transactionTypes.find(t => t.id === transaction.transaction_type)?.name || 'Unassigned'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="pagination">
        {renderPaginationButtons()}
      </div>
    </div>
  );
}

export default TransactionList;