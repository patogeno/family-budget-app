import React, { useState, useEffect } from 'react';
import { getTransactions } from '../../services/api';

function TransactionList() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      const response = await getTransactions();
      setTransactions(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch transactions');
      setLoading(false);
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

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="transaction-list">
      <h2>Transactions</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Amount</th>
            <th>Account</th>
            <th>Budget Group</th>
            <th>Transaction Type</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction) => (
            <tr key={transaction.id}>
              <td>{transaction.date}</td>
              <td>{transaction.description}</td>
              <td className={getAmountClass(transaction.amount)}>{transaction.amount}</td>
              <td>{transaction.account_name}</td>
              <td>{transaction.budget_group}</td>
              <td>{transaction.transaction_type}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TransactionList;