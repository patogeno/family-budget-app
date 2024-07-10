import React, { useState, useEffect } from 'react';
import { importTransactionPatterns, getAccountNames } from '../../services/api';

function TransactionPatternImport() {
  const [file, setFile] = useState(null);
  const [accountName, setAccountName] = useState('');
  const [accountNames, setAccountNames] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [fileName, setFileName] = useState('No file chosen');

  useEffect(() => {
    fetchAccountNames();
  }, []);

  const fetchAccountNames = async () => {
    try {
      const response = await getAccountNames();
      setAccountNames(response.data);
    } catch (error) {
      console.error('Error fetching account names:', error);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setFile(file);
    setFileName(file ? file.name : 'No file chosen');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('account_name', accountName);

    try {
      const response = await importTransactionPatterns(formData);
      setMessage(response.data.message);
    } catch (error) {
      setMessage('Failed to import transaction patterns');
    }

    setLoading(false);
  };

  return (
    <div className="content">
      <form onSubmit={handleSubmit} className="import-form">
        <h2>Import Transaction Patterns</h2>
        <div className="form-group file-input-wrapper">
          <label htmlFor="file" className="file-label">Choose file</label>
          <span className="file-name">{fileName}</span>
          <input 
            type="file" 
            id="file" 
            onChange={handleFileChange} 
            required 
          />
        </div>
        <div className="form-group">
          <label htmlFor="accountName">Account Name:</label>
          <select 
            id="accountName" 
            value={accountName} 
            onChange={(e) => setAccountName(e.target.value)}
            required
          >
            <option value="">Select Account Name</option>
            {accountNames.map(account => (
              <option key={account.id} value={account.id}>
                {account.name}
              </option>
            ))}
          </select>
        </div>
        <button type="submit" className="import-button" disabled={loading}>
          {loading ? 'Importing...' : 'Import'}
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default TransactionPatternImport;