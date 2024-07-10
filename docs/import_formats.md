# Bank Import Formats

The application supports multiple bank import formats. The order of the formats in the .env file is crucial as it corresponds to the explanation below.

## Supported Formats

### Bank Import Format 1:
- Description: Debit account export
- File type: CSV
- Headers: No
- Data start: Row 1
- Columns (in order):
  1. Date (format: DD/MM/YYYY)
  2. Amount (format: $X,XXX.XX or simpler without $ or ,)
  3. Description
  4. Balance (format: $X,XXX.XX or simpler without $ or ,)

### Bank Import Format 2:
- Description: Credit account export
- File type: CSV
- Headers: No
- Data start: Row 1
- Columns (in order):
  1. Date (format: DD/MM/YYYY)
  2. Amount (format: $X,XXX.XX or simpler without $ or ,)
  3. Description

### Bank Import Format 3:
- Description: General account export
- File type: CSV
- Headers: No
- Data start: Row 3 (first two rows are skipped)
- Columns (in order):
  1. Date (format: DD/MM/YYYY)
  2. Description
  3. Amount (format: $X,XXX.XX or simpler without $ or ,)
  4. Balance (format: $X,XXX.XX or simpler without $ or ,)

Note: All amount and balance values are assumed to use commas as thousand separators 
and periods as decimal separators. The dollar sign ($) can be present in the original data.

## Configuration

The supported bank formats must be defined in the .env file using the BANK_FORMATS variable. 
The order of the formats in this variable must match the order of the explanations above.

Example:

```
BANK_FORMATS={
    "alpha_bank_debit": "Alpha Bank Debit",
    "beta_bank_credit": "Beta Bank Credit",
    "gamma_bank_checking": "Gamma Bank Checking"
}
```

In this example:
- "alpha_bank_debit" corresponds to Bank Import Format 1
- "beta_bank_credit" corresponds to Bank Import Format 2
- "gamma_bank_checking" corresponds to Bank Import Format 3