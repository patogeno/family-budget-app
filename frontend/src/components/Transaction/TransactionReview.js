import React, { useState, useEffect, useCallback, useRef } from 'react';
import { getTransactions, reviewTransactions, redoCategorization, getTransactionTypes, getBudgetGroups, modifyTransaction, getAccountNames } from '../../services/api';

function TransactionReview() {
  const [transactions, setTransactions] = useState([]);
  const [filteredTransactions, setFilteredTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');
  const [selectedTransactions, setSelectedTransactions] = useState([]);
  const [transactionTypes, setTransactionTypes] = useState([]);
  const [budgetGroups, setBudgetGroups] = useState([]);
  const [accountNames, setAccountNames] = useState([]);

  // Add a ref to store cursor positions
  const cursorPositions = useRef({});

  // Add state for filters
  const [filters, setFilters] = useState({
    description: '',
    type: '',
    budget: '',
    comments: ''
  });

  const applyFilters = useCallback(() => {
    let filtered = transactions;

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

    if (filters.comments) {
      filtered = filtered.filter(t => 
        t.comments && t.comments.toLowerCase().includes(filters.comments.toLowerCase())
      );
    }

    setFilteredTransactions(filtered);
  }, [transactions, filters]);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [applyFilters]);

  const fetchData = async () => {
    try {
      const [transactionsResponse, typesResponse, groupsResponse, accountsResponse] = await Promise.all([
        getTransactions('pending_review'),
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

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const clearAllFilters = () => {
    setFilters({
      description: '',
      type: '',
      budget: '',
      comments: ''
    });
  };

  const handleSelect = (id) => {
    setSelectedTransactions(prev => 
      prev.includes(id) ? prev.filter(t => t !== id) : [...prev, id]
    );
  };

  const handleBulkConfirm = async () => {
    try {
      await reviewTransactions({ transaction_ids: selectedTransactions });
      setTransactions(prev => prev.filter(t => !selectedTransactions.includes(t.id)));
      setSelectedTransactions([]);
    } catch (err) {
      setError('Failed to confirm transactions');
    }
  };

  const handleRedoCategorization = async () => {
    try {
      const response = await redoCategorization();
      setTransactions(response.data);
    } catch (err) {
      setError('Failed to redo categorization');
    }
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

  const handleTypeChange = (id, value) => {
    setTransactions(prev => prev.map(t => 
      t.id === id ? {...t, transaction_type: value, transaction_assignment_type: 'manual'} : t
    ));
  };

  const handleBudgetChange = (id, value) => {
    setTransactions(prev => prev.map(t => 
      t.id === id ? {...t, budget_group: value, budget_group_assignment_type: 'manual'} : t
    ));
  };

  const handleCommentChange = (id, value, cursorPosition) => {
    setTransactions(prev => prev.map(t => 
      t.id === id ? {...t, comments: value} : t
    ));
    // Store the cursor position
    cursorPositions.current[id] = cursorPosition;
  };

  // Use this effect to restore cursor positions after render
  useEffect(() => {
    Object.keys(cursorPositions.current).forEach(id => {
      const input = document.querySelector(`input[name="comments-${id}"]`);
      if (input) {
        input.setSelectionRange(cursorPositions.current[id], cursorPositions.current[id]);
      }
    });
  });

  const handleModify = async (id) => {
    const transaction = transactions.find(t => t.id === id);
    try {
      const response = await modifyTransaction(id, {
        transaction_type: transaction.transaction_type,
        budget_group: transaction.budget_group,
        comments: transaction.comments
      });
      
      if (response.data.success) {
        setTransactions(prev => prev.filter(t => t.id !== id));
        setMessage(response.data.message);
        // Clear the message after 3 seconds
        setTimeout(() => setMessage(''), 3000);
      } else {
        setError(`Failed to modify transaction: ${response.data.error}`);
      }
    } catch (err) {
      setError(`Failed to modify transaction: ${err.response?.data?.error || err.message}`);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="transaction-review">
      <h2>Review Transactions</h2>
      {message && <p className="success-message">{message}</p>}
      <div className="bulk-actions">
        <button onClick={handleBulkConfirm} disabled={selectedTransactions.length === 0}>
          Bulk Confirm
        </button>
        <button onClick={handleRedoCategorization}>Redo Categorization</button>
      </div>
      <div className="filters">
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
        <input
          type="text"
          name="comments"
          placeholder="Filter by comments"
          value={filters.comments}
          onChange={handleFilterChange}
        />
        <button onClick={clearAllFilters} className="clear-filters-btn">Clear All Filters</button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Amount</th>
            <th>Account</th>
            <th>Type</th>
            <th></th>
            <th>Budget</th>
            <th></th>
            <th>Select</th>
            <th>Comments</th>
            <th>Modify</th>
          </tr>
        </thead>
        <tbody>
          {filteredTransactions.map((transaction) => (
            <tr key={transaction.id}>
              <td>{transaction.date}</td>
              <td>{transaction.description}</td>
              <td className={getAmountClass(transaction.amount)}>{transaction.amount}</td>
              <td>{accountNames.find(a => a.id === transaction.account_name)?.name || 'Unknown'}</td>
              <td>
                <select
                  value={transaction.transaction_type || ''}
                  onChange={(e) => handleTypeChange(transaction.id, e.target.value)}
                >
                  <option value="">Select Transaction Type</option>
                  {transactionTypes.map(type => (
                    <option key={type.id} value={type.id}>{type.name}</option>
                  ))}
                </select>
              </td>
              <td>
                {transaction.transaction_assignment_type === 'auto_unchecked' && <i className="fas fa-robot" title="Auto Unchecked"></i>}
                {transaction.transaction_assignment_type === 'auto_checked' && <i className="fas fa-check-circle" title="Auto Checked"></i>}
                {transaction.transaction_assignment_type === 'manual' && <i className="fas fa-user" title="Manual"></i>}
              </td>
              <td>
                <select
                  value={transaction.budget_group || ''}
                  onChange={(e) => handleBudgetChange(transaction.id, e.target.value)}
                >
                  <option value="">Select Budget Group</option>
                  {budgetGroups.map(group => (
                    <option key={group.id} value={group.id}>{group.name}</option>
                  ))}
                </select>
              </td>
              <td>
                {transaction.budget_group_assignment_type === 'auto_unchecked' && <i className="fas fa-robot" title="Auto Unchecked"></i>}
                {transaction.budget_group_assignment_type === 'auto_checked' && <i className="fas fa-check-circle" title="Auto Checked"></i>}
                {transaction.budget_group_assignment_type === 'manual' && <i className="fas fa-user" title="Manual"></i>}
              </td>
              <td>
                <input 
                  type="checkbox" 
                  checked={selectedTransactions.includes(transaction.id)}
                  onChange={() => handleSelect(transaction.id)}
                />
              </td>
              <td>
                <input
                  type="text"
                  name={`comments-${transaction.id}`}
                  value={transaction.comments || ''}
                  onChange={(e) => handleCommentChange(transaction.id, e.target.value, e.target.selectionStart)}
                />
              </td>
              <td>
                <button onClick={() => handleModify(transaction.id)}>Modify</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TransactionReview;