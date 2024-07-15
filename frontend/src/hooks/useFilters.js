import { useState, useRef, useEffect } from 'react';

export const useFilters = (initialFilters) => {
  const [filters, setFilters] = useState(initialFilters);
  const [dateInputs, setDateInputs] = useState({
    dateFrom: '',
    dateTo: ''
  });
  const dateTimeoutRef = useRef(null);

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleDateInputChange = (name, value) => {
    setDateInputs(prev => ({ ...prev, [name]: value }));

    if (dateTimeoutRef.current) {
      clearTimeout(dateTimeoutRef.current);
    }

    dateTimeoutRef.current = setTimeout(() => {
      handleFilterChange(name, value);
    }, 700);
  };

  const applyDateFilter = (name, value) => {
    if (dateTimeoutRef.current) {
      clearTimeout(dateTimeoutRef.current);
    }
    handleFilterChange(name, value);
  };

  const clearAllFilters = () => {
    setFilters(initialFilters);
    setDateInputs({
      dateFrom: '',
      dateTo: ''
    });
  };

  useEffect(() => {
    return () => {
      if (dateTimeoutRef.current) {
        clearTimeout(dateTimeoutRef.current);
      }
    };
  }, []);

  return {
    filters,
    dateInputs,
    handleFilterChange,
    handleDateInputChange,
    applyDateFilter,
    clearAllFilters
  };
};