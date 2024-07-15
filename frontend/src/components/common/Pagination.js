import React from 'react';

export const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  const renderPaginationButtons = () => {
    let buttons = [];

    if (totalPages <= 10) {
      for (let i = 1; i <= totalPages; i++) {
        buttons.push(
          <button key={i} onClick={() => onPageChange(i)} className={currentPage === i ? 'active' : ''}>
            {i}
          </button>
        );
      }
    } else {
      buttons.push(
        <button key={1} onClick={() => onPageChange(1)} className={currentPage === 1 ? 'active' : ''}>
          1
        </button>
      );

      if (currentPage > 4) {
        buttons.push(<span key="ellipsis1">...</span>);
      }

      for (let i = Math.max(2, currentPage - 2); i <= Math.min(totalPages - 1, currentPage + 2); i++) {
        buttons.push(
          <button key={i} onClick={() => onPageChange(i)} className={currentPage === i ? 'active' : ''}>
            {i}
          </button>
        );
      }

      if (currentPage < totalPages - 3) {
        buttons.push(<span key="ellipsis2">...</span>);
      }

      buttons.push(
        <button key={totalPages} onClick={() => onPageChange(totalPages)} className={currentPage === totalPages ? 'active' : ''}>
          {totalPages}
        </button>
      );
    }

    return buttons;
  };

  return (
    <div className="pagination">
      {renderPaginationButtons()}
    </div>
  );
};