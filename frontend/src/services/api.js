import axios from 'axios';

const API_URL = 'http://localhost:8000/api/';

const api = axios.create({
  baseURL: API_URL,
});

export const getTransactions = (filter = '') => {
  const endpoint = filter === 'pending_review' ? 'transactions/pending_review/' : 'transactions/';
  return api.get(endpoint);
};
export const importTransactions = (data) => api.post('import-transactions/', data);
export const reviewTransactions = (data) => api.post('transactions/bulk_confirm/', data);
export const redoCategorization = () => api.post('transactions/redo_categorization/');
export const importTransactionPatterns = (data) => api.post('import-transaction-patterns/', data);
export const getAccountNames = () => api.get('account-names/');
export const getTransactionTypes = () => api.get('transaction-types/');
export const getBudgetGroups = () => api.get('budget-groups/');
export const modifyTransaction = (id, data) => api.post(`transactions/${id}/modify/`, data);
export const getBankFormats = () => api.get('bank-formats/');

export default api;