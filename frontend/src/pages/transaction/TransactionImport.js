import React, { useState, useEffect } from 'react';
import { importTransactions, getAccountNames, getBankFormats  } from '../../services/api';

function TransactionImport() {
  const [file, setFile] = useState(null);
  const [importFormat, setImportFormat] = useState('');
  const [accountName, setAccountName] = useState('');
  const [newAccountName, setNewAccountName] = useState('');
  const [accountNames, setAccountNames] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [fileName, setFileName] = useState('No file chosen');
  const [bankFormats, setBankFormats] = useState({});

  useEffect(() => {
    fetchAccountNames();
    fetchBankFormats();
  }, []);

  const fetchAccountNames = async () => {
    try {
      const response = await getAccountNames();
      setAccountNames(response.data);
    } catch (error) {
      console.error('Error fetching account names:', error);
    }
  };

  const fetchBankFormats = async () => {
    try {
      const response = await getBankFormats();
      setBankFormats(response.data);
    } catch (error) {
      console.error('Error fetching bank formats:', error);
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
    formData.append('import_format', importFormat);
    
    // If a new account name is provided, use that. Otherwise, use the selected account.
    if (newAccountName) {
      formData.append('new_account_name', newAccountName);
    } else {
      formData.append('account_name', accountName);
    }

    try {
      const response = await importTransactions(formData);
      setMessage(response.data.message);
    } catch (error) {
      setMessage('Failed to import transactions');
    }

    setLoading(false);
  };

  return (
    <div className="content">
      <form onSubmit={handleSubmit} className="import-form">
        <h2>Import Transactions</h2>
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
          <label htmlFor="importFormat">Import Format:</label>
          <select 
            id="importFormat" 
            value={importFormat} 
            onChange={(e) => setImportFormat(e.target.value)}
            required
          >
            <option value="">Select format</option>
            {Object.entries(bankFormats).map(([format, name]) => (
              <option key={format} value={format}>{name}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="accountName">Account Name:</label>
          <select 
            id="accountName" 
            value={accountName} 
            onChange={(e) => setAccountName(e.target.value)}
          >
            <option value="">Select Account Name</option>
            {accountNames.map(account => (
              <option key={account.id} value={account.id}>{account.name}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="newAccountName">New Account Name:</label>
          <input 
            type="text" 
            id="newAccountName" 
            value={newAccountName} 
            onChange={(e) => setNewAccountName(e.target.value)} 
            placeholder="Enter new account name"
          />
        </div>
        <button type="submit" className="import-button" disabled={loading}>
          {loading ? 'Importing...' : 'Import'}
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default TransactionImport;