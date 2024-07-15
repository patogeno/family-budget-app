import { useState } from 'react';

export const usePagination = (itemsPerPageOptions = [10, 25, 50, 100]) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(itemsPerPageOptions[0]);
  const [totalPages, setTotalPages] = useState(0);

  const handlePageChange = (page) => setCurrentPage(page);
  const handleItemsPerPageChange = (newItemsPerPage) => {
    setItemsPerPage(Number(newItemsPerPage));
    setCurrentPage(1);
  };

  return {
    currentPage,
    itemsPerPage,
    totalPages,
    setTotalPages,
    handlePageChange,
    handleItemsPerPageChange,
    itemsPerPageOptions
  };
};