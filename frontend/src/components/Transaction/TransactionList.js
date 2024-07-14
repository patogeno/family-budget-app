import React, { useState, useEffect, useCallback } from 'react';
import { getPaginatedTransactions, getTransactionTypes, getBudgetGroups, getAccountNames } from '../../services/api';

function TransactionList() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [transactionTypes, setTransactionTypes] = useState([]);
  const [budgetGroups, setBudgetGroups] = useState([]);
  const [accountNames, setAccountNames] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [transactionsPerPage, setTransactionsPerPage] = useState(10);
  const [totalPages, setTotalPages] = useState(0);
  const [sortConfig, setSortConfig] = useState({ key: 'date', direction: 'desc' });
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    description: '',
    type: '',
    budget: '',
    account: ''
  });

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        page: currentPage,
        per_page: transactionsPerPage,
        sort_by: sortConfig.key,
        sort_direction: sortConfig.direction,
        dateFrom: filters.dateFrom,
        dateTo: filters.dateTo,
        description: filters.description,
        type: filters.type,
        budget: filters.budget,
        account: filters.account
      };
      const response = await getPaginatedTransactions(params);
      setTransactions(response.data.transactions);
      setTotalPages(response.data.total_pages);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch transactions');
      setLoading(false);
    }
  }, [currentPage, transactionsPerPage, sortConfig, filters]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [typesResponse, groupsResponse, accountsResponse] = await Promise.all([
          getTransactionTypes(),
          getBudgetGroups(),
          getAccountNames()
        ]);
        setTransactionTypes(typesResponse.data);
        setBudgetGroups(groupsResponse.data);
        setAccountNames(accountsResponse.data);
      } catch (err) {
        setError('Failed to fetch data');
      }
    };
    fetchData();
  }, []);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
    setCurrentPage(1);  // Reset to first page when changing filters
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
    setCurrentPage(1);
  };

  const handleSort = (key) => {
    setSortConfig(prevConfig => ({
      key,
      direction: prevConfig.key === key && prevConfig.direction === 'asc' ? 'desc' : 'asc',
    }));
    setCurrentPage(1);
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

  const renderPaginationButtons = () => {
    let buttons = [];

    if (totalPages <= 10) {
      for (let i = 1; i <= totalPages; i++) {
        buttons.push(
          <button key={i} onClick={() => setCurrentPage(i)} className={currentPage === i ? 'active' : ''}>
            {i}
          </button>
        );
      }
    } else {
      buttons.push(
        <button key={1} onClick={() => setCurrentPage(1)} className={currentPage === 1 ? 'active' : ''}>
          1
        </button>
      );

      if (currentPage > 4) {
        buttons.push(<span key="ellipsis1">...</span>);
      }

      for (let i = Math.max(2, currentPage - 2); i <= Math.min(totalPages - 1, currentPage + 2); i++) {
        buttons.push(
          <button key={i} onClick={() => setCurrentPage(i)} className={currentPage === i ? 'active' : ''}>
            {i}
          </button>
        );
      }

      if (currentPage < totalPages - 3) {
        buttons.push(<span key="ellipsis2">...</span>);
      }

      buttons.push(
        <button key={totalPages} onClick={() => setCurrentPage(totalPages)} className={currentPage === totalPages ? 'active' : ''}>
          {totalPages}
        </button>
      );
    }

    return buttons;
  };

  const handleTransactionsPerPageChange = (e) => {
    setTransactionsPerPage(Number(e.target.value));
    setCurrentPage(1);
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
            <th onClick={() => handleSort('date')}>Date {sortConfig.key === 'date' && (sortConfig.direction === 'asc' ? '▲' : '▼')}</th>
            <th onClick={() => handleSort('description')}>Description {sortConfig.key === 'description' && (sortConfig.direction === 'asc' ? '▲' : '▼')}</th>
            <th onClick={() => handleSort('amount')}>Amount {sortConfig.key === 'amount' && (sortConfig.direction === 'asc' ? '▲' : '▼')}</th>
            <th onClick={() => handleSort('account_name')}>Account {sortConfig.key === 'account_name' && (sortConfig.direction === 'asc' ? '▲' : '▼')}</th>
            <th onClick={() => handleSort('budget_group')}>Budget Group {sortConfig.key === 'budget_group' && (sortConfig.direction === 'asc' ? '▲' : '▼')}</th>
            <th onClick={() => handleSort('transaction_type')}>Transaction Type {sortConfig.key === 'transaction_type' && (sortConfig.direction === 'asc' ? '▲' : '▼')}</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction) => (
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