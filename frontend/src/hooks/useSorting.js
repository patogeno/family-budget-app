import { useState } from 'react';

export const useSorting = (initialKey = 'date', initialDirection = 'desc') => {
  const [sortConfig, setSortConfig] = useState({ key: initialKey, direction: initialDirection });

  const handleSort = (key) => {
    setSortConfig(prevConfig => ({
      key,
      direction: prevConfig.key === key && prevConfig.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  return { sortConfig, handleSort };
};