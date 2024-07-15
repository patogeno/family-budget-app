import React from 'react';

export const Filters = ({
  filters,
  dateInputs,
  transactionTypes,
  budgetGroups,
  accountNames,
  onFilterChange,
  onDateInputChange,
  onDateFilterApply,
  onClearFilters,
  itemsPerPage,
  itemsPerPageOptions,
  onItemsPerPageChange
}) => {
  return (
    <div className="filters">
      <input
        type="date"
        name="dateFrom"
        value={dateInputs.dateFrom}
        onChange={(e) => onDateInputChange('dateFrom', e.target.value)}
        onBlur={(e) => onDateFilterApply('dateFrom', e.target.value)}
      />
      <input
        type="date"
        name="dateTo"
        value={dateInputs.dateTo}
        onChange={(e) => onDateInputChange('dateTo', e.target.value)}
        onBlur={(e) => onDateFilterApply('dateTo', e.target.value)}
      />
      <input
        type="text"
        name="description"
        placeholder="Filter by description"
        value={filters.description}
        onChange={(e) => onFilterChange('description', e.target.value)}
      />
      <select
        name="type"
        value={filters.type}
        onChange={(e) => onFilterChange('type', e.target.value)}
      >
        <option value="">All Types</option>
        {transactionTypes.map(type => (
          <option key={type.id} value={type.id}>{type.name}</option>
        ))}
      </select>
      <select
        name="budget"
        value={filters.budget}
        onChange={(e) => onFilterChange('budget', e.target.value)}
      >
        <option value="">All Budgets</option>
        {budgetGroups.map(group => (
          <option key={group.id} value={group.id}>{group.name}</option>
        ))}
      </select>
      <select
        name="account"
        value={filters.account}
        onChange={(e) => onFilterChange('account', e.target.value)}
      >
        <option value="">All Accounts</option>
        {accountNames.map(account => (
          <option key={account.id} value={account.id}>{account.name}</option>
        ))}
      </select>
      <button onClick={onClearFilters} className="clear-filters-btn">Clear All Filters</button>
      <select
        value={itemsPerPage}
        onChange={(e) => onItemsPerPageChange(e.target.value)}
        className="transactions-per-page"
      >
        {itemsPerPageOptions.map(option => (
          <option key={option} value={option}>{option} per page</option>
        ))}
      </select>
    </div>
  );
};