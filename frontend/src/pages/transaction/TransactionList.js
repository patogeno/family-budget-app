import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { getPaginatedTransactions, getTransactionTypes, getBudgetGroups, getAccountNames } from '../../services/api';
import { usePagination } from '../../hooks/usePagination';
import { useSorting } from '../../hooks/useSorting';
import { useFilters } from '../../hooks/useFilters';
import { Pagination } from '../../components/common/Pagination';
import { Filters } from '../../components/common/Filters';
import debounce from 'lodash/debounce';

function TransactionList() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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
    account: ''
  });

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        page: currentPage,
        per_page: itemsPerPage,
        sort_by: sortConfig.key,
        sort_direction: sortConfig.direction,
        ...filters
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

  const getAmountClass = (amount) => {
    const numericAmount = parseFloat(amount);
    if (numericAmount > 0) return 'amount-positive';
    if (numericAmount < -500) return 'amount-negative-high';
    if (numericAmount < -150) return 'amount-negative-medium';
    return '';
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="transaction-list">
      <h2>Transactions</h2>
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
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={handlePageChange}
      />
    </div>
  );
}

export default TransactionList;