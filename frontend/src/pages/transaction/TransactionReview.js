import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { getPaginatedTransactions, redoCategorization, getTransactionTypes, getBudgetGroups, modifyTransaction, getAccountNames } from '../../services/api';
import { usePagination } from '../../hooks/usePagination';
import { useSorting } from '../../hooks/useSorting';
import { useFilters } from '../../hooks/useFilters';
import { Pagination } from '../../components/common/Pagination';
import { Filters } from '../../components/common/Filters';
import debounce from 'lodash/debounce';

function TransactionReview() {
  const [transactions, setTransactions] = useState([]);
  const [modifiedTransactions, setModifiedTransactions] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');
  const [selectedTransactions, setSelectedTransactions] = useState([]);
  const [transactionTypes, setTransactionTypes] = useState([]);
  const [budgetGroups, setBudgetGroups] = useState([]);
  const [accountNames, setAccountNames] = useState([]);

  const { 
    currentPage, 
    itemsPerPage, 
    totalPages, 
    setTotalPages, 
    handlePageChange, 
    handleItemsPerPageChange, 
    itemsPerPageOptions 
  } = usePagination();

  const { sortConfig, handleSort } = useSorting('date', 'desc');

  const { 
    filters, 
    dateInputs, 
    handleFilterChange, 
    handleDateInputChange, 
    applyDateFilter, 
    clearAllFilters 
  } = useFilters({
    dateFrom: '',
    dateTo: '',
    description: '',
    type: '',
    budget: '',
    account: '',
    comments: ''
  });

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        page: currentPage,
        per_page: itemsPerPage,
        sort_by: sortConfig.key,
        sort_direction: sortConfig.direction,
        ...filters,
        review_status: 'pending'
      };
      const response = await getPaginatedTransactions(params);
      setTransactions(response.data.transactions);
      setTotalPages(response.data.total_pages);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch transactions');
      setLoading(false);
    }
  }, [currentPage, itemsPerPage, sortConfig.key, sortConfig.direction, filters, setTotalPages]);

  const debouncedFetchTransactions = useMemo(
    () => debounce(fetchTransactions, 700),
    [fetchTransactions]
  );

  useEffect(() => {
    debouncedFetchTransactions();
    return () => debouncedFetchTransactions.cancel();
  }, [debouncedFetchTransactions]);

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

  const handleSelect = (id) => {
    setSelectedTransactions(prev => 
      prev.includes(id) ? prev.filter(t => t !== id) : [...prev, id]
    );
  };

  const handleModificationChange = (id, field, value) => {
    setModifiedTransactions(prev => ({
      ...prev,
      [id]: {
        ...prev[id],
        [field]: value,
        isModified: true
      }
    }));
  };

  const handleConfirm = async (id) => {
    const transaction = transactions.find(t => t.id === id);
    const modifiedData = modifiedTransactions[id] || {};
    
    let newStatus;
    let updateData;

    if (modifiedData.isModified) {
      newStatus = 'modified';
      updateData = { ...modifiedData, review_status: newStatus };
      delete updateData.isModified;
    } else if (transaction.review_status !== 'confirmed') {
      newStatus = 'confirmed';
      updateData = { review_status: newStatus };
    } else {
      // Transaction is already confirmed and not modified, no action needed
      return;
    }

    try {
      await modifyTransaction(id, updateData);
      fetchTransactions(); // Refresh the list after modification
      setModifiedTransactions(prev => {
        const newState = { ...prev };
        delete newState[id];
        return newState;
      });
      setMessage(`Transaction ${newStatus} successfully`);
    } catch (err) {
      setError(`Failed to update transaction: ${err.response?.data?.error || err.message}`);
    }
  };

  const handleBulkConfirm = async () => {
    try {
      const bulkModifications = selectedTransactions.map(id => {
        transactions.find(t => t.id === id);
        const modifiedData = modifiedTransactions[id] || {};
        
        let updateData;
        if (modifiedData.isModified) {
          updateData = { ...modifiedData, review_status: 'modified' };
          delete updateData.isModified;
        } else {
          updateData = { review_status: 'confirmed' };
        }

        return { id, ...updateData };
      });

      await Promise.all(bulkModifications.map(mod => modifyTransaction(mod.id, mod)));
      fetchTransactions(); // Refresh the list after bulk confirm
      setSelectedTransactions([]);
      setModifiedTransactions({});
      setMessage('Transactions updated successfully');
    } catch (err) {
      setError('Failed to update transactions');
    }
  };

  const handleRedoCategorization = async () => {
    try {
      await redoCategorization();
      fetchTransactions(); // Refresh the list after re-categorization
      setMessage('Re-categorization completed successfully');
    } catch (err) {
      setError('Failed to redo categorization');
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
      <Filters
        filters={filters}
        dateInputs={dateInputs}
        transactionTypes={transactionTypes}
        budgetGroups={budgetGroups}
        accountNames={accountNames}
        onFilterChange={handleFilterChange}
        onDateInputChange={handleDateInputChange}
        onDateFilterApply={applyDateFilter}
        onClearFilters={clearAllFilters}
        itemsPerPage={itemsPerPage}
        itemsPerPageOptions={itemsPerPageOptions}
        onItemsPerPageChange={handleItemsPerPageChange}
      />
      <table>
        <thead>
          <tr>
            <th onClick={() => handleSort('date')}>Date {sortConfig.key === 'date' && (sortConfig.direction === 'asc' ? '▲' : '▼')}</th>
            <th onClick={() => handleSort('description')}>Description {sortConfig.key === 'description' && (sortConfig.direction === 'asc' ? '▲' : '▼')}</th>
            <th onClick={() => handleSort('amount')}>Amount {sortConfig.key === 'amount' && (sortConfig.direction === 'asc' ? '▲' : '▼')}</th>
            <th onClick={() => handleSort('account_name')}>Account {sortConfig.key === 'account_name' && (sortConfig.direction === 'asc' ? '▲' : '▼')}</th>
            <th>Type</th>
            <th>Budget</th>
            <th>Select</th>
            <th>Comments</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction) => (
            <tr key={transaction.id}>
              <td>{transaction.date}</td>
              <td>{transaction.description}</td>
              <td>{transaction.amount}</td>
              <td>{accountNames.find(a => a.id === transaction.account_name)?.name || 'Unknown'}</td>
              <td>
                <select
                  value={modifiedTransactions[transaction.id]?.transaction_type || transaction.transaction_type || ''}
                  onChange={(e) => handleModificationChange(transaction.id, 'transaction_type', e.target.value)}
                >
                  <option value="">Select Type</option>
                  {transactionTypes.map(type => (
                    <option key={type.id} value={type.id}>{type.name}</option>
                  ))}
                </select>
              </td>
              <td>
                <select
                  value={modifiedTransactions[transaction.id]?.budget_group || transaction.budget_group || ''}
                  onChange={(e) => handleModificationChange(transaction.id, 'budget_group', e.target.value)}
                >
                  <option value="">Select Budget</option>
                  {budgetGroups.map(group => (
                    <option key={group.id} value={group.id}>{group.name}</option>
                  ))}
                </select>
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
                  value={modifiedTransactions[transaction.id]?.comments || transaction.comments || ''}
                  onChange={(e) => handleModificationChange(transaction.id, 'comments', e.target.value)}
                />
              </td>
              <td>
                <button onClick={() => handleConfirm(transaction.id)}>
                  {modifiedTransactions[transaction.id]?.isModified ? 'Save & Confirm' : 'Confirm'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={handlePageChange}
      />
    </div>
  );
}

export default TransactionReview;