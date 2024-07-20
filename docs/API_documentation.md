# Family Budget API

Version: v1

API documentation for the Family Budget Management App

## /account-names/

### GET

account-names_list

API endpoint that allows account names to be viewed or edited.

#### Responses

**200**



### POST

account-names_create

API endpoint that allows account names to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**201**



### PARAMETERS

---

## /account-names/{id}/

### GET

account-names_read

API endpoint that allows account names to be viewed or edited.

#### Responses

**200**



### PUT

account-names_update

API endpoint that allows account names to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### PATCH

account-names_partial_update

API endpoint that allows account names to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### DELETE

account-names_delete

API endpoint that allows account names to be viewed or edited.

#### Responses

**204**



### PARAMETERS

---

## /bank-formats/

### GET

bank-formats_list

Get all available bank formats

#### Responses

**200**



### PARAMETERS

---

## /budget-adjustments/

### GET

budget-adjustments_list

API endpoint that allows budget adjustments to be viewed or edited.

#### Responses

**200**



### POST

budget-adjustments_create

API endpoint that allows budget adjustments to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**201**



### PARAMETERS

---

## /budget-adjustments/{id}/

### GET

budget-adjustments_read

API endpoint that allows budget adjustments to be viewed or edited.

#### Responses

**200**



### PUT

budget-adjustments_update

API endpoint that allows budget adjustments to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### PATCH

budget-adjustments_partial_update

API endpoint that allows budget adjustments to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### DELETE

budget-adjustments_delete

API endpoint that allows budget adjustments to be viewed or edited.

#### Responses

**204**



### PARAMETERS

---

## /budget-groups/

### GET

budget-groups_list

API endpoint that allows budget groups to be viewed or edited.

#### Responses

**200**



### POST

budget-groups_create

API endpoint that allows budget groups to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**201**



### PARAMETERS

---

## /budget-groups/{id}/

### GET

budget-groups_read

API endpoint that allows budget groups to be viewed or edited.

#### Responses

**200**



### PUT

budget-groups_update

API endpoint that allows budget groups to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### PATCH

budget-groups_partial_update

API endpoint that allows budget groups to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### DELETE

budget-groups_delete

API endpoint that allows budget groups to be viewed or edited.

#### Responses

**204**



### PARAMETERS

---

## /budget-initializations/

### GET

budget-initializations_list

API endpoint that allows budget initializations to be viewed or edited.

#### Responses

**200**



### POST

budget-initializations_create

API endpoint that allows budget initializations to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**201**



### PARAMETERS

---

## /budget-initializations/{id}/

### GET

budget-initializations_read

API endpoint that allows budget initializations to be viewed or edited.

#### Responses

**200**



### PUT

budget-initializations_update

API endpoint that allows budget initializations to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### PATCH

budget-initializations_partial_update

API endpoint that allows budget initializations to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### DELETE

budget-initializations_delete

API endpoint that allows budget initializations to be viewed or edited.

#### Responses

**204**



### PARAMETERS

---

## /create-adjustment-transaction/

### POST

create-adjustment-transaction_create

Create an adjustment transaction

#### Parameters

- `data` (body): No description provided

#### Responses

**201**

Adjustment transactions created successfully

### PARAMETERS

---

## /import-transaction-patterns/

### POST

import-transaction-patterns_create

Import transaction patterns from a CSV file

#### Parameters

- `data` (body): No description provided

#### Responses

**201**

Transaction patterns imported successfully

**400**

Bad request

### PARAMETERS

---

## /import-transactions/

### POST

import-transactions_create

Import transactions from a CSV file

#### Parameters

- `data` (body): No description provided

#### Responses

**201**

Transactions imported successfully

**400**

Bad request

### PARAMETERS

---

## /paginated-transactions/

### GET

paginated-transactions_list

Get paginated and filtered transactions

#### Parameters

- `page` (query): Page number
- `per_page` (query): Number of items per page
- `sort_by` (query): Field to sort by
- `sort_direction` (query): Sort direction (asc or desc)
- `dateFrom` (query): Start date for filtering (YYYY-MM-DD)
- `dateTo` (query): End date for filtering (YYYY-MM-DD)
- `description` (query): Filter by description
- `type` (query): Filter by transaction type ID
- `budget` (query): Filter by budget group ID
- `account` (query): Filter by account ID
- `review_status` (query): Filter by review status

#### Responses

**200**

Successful response

### PARAMETERS

---

## /transaction-patterns/

### GET

transaction-patterns_list

API endpoint that allows transaction patterns to be viewed or edited.

#### Responses

**200**



### POST

transaction-patterns_create

API endpoint that allows transaction patterns to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**201**



### PARAMETERS

---

## /transaction-patterns/{id}/

### GET

transaction-patterns_read

API endpoint that allows transaction patterns to be viewed or edited.

#### Responses

**200**



### PUT

transaction-patterns_update

API endpoint that allows transaction patterns to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### PATCH

transaction-patterns_partial_update

API endpoint that allows transaction patterns to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### DELETE

transaction-patterns_delete

API endpoint that allows transaction patterns to be viewed or edited.

#### Responses

**204**



### PARAMETERS

---

## /transaction-types/

### GET

transaction-types_list

API endpoint that allows transaction types to be viewed or edited.

#### Responses

**200**



### POST

transaction-types_create

API endpoint that allows transaction types to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**201**



### PARAMETERS

---

## /transaction-types/{id}/

### GET

transaction-types_read

API endpoint that allows transaction types to be viewed or edited.

#### Responses

**200**



### PUT

transaction-types_update

API endpoint that allows transaction types to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### PATCH

transaction-types_partial_update

API endpoint that allows transaction types to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### DELETE

transaction-types_delete

API endpoint that allows transaction types to be viewed or edited.

#### Responses

**204**



### PARAMETERS

---

## /transactions/

### GET

transactions_list

API endpoint that allows transactions to be viewed or edited.

#### Responses

**200**



### POST

transactions_create

API endpoint that allows transactions to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**201**



### PARAMETERS

---

## /transactions/bulk_confirm/

### POST

transactions_bulk_confirm

Confirm multiple transactions

#### Parameters

- `data` (body): No description provided

#### Responses

**200**

Transactions confirmed successfully

### PARAMETERS

---

## /transactions/pending_review/

### GET

transactions_pending_review

List transactions pending review

#### Responses

**200**



### PARAMETERS

---

## /transactions/redo_categorization/

### POST

transactions_redo_categorization

Redo categorization for uncategorized transactions

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### PARAMETERS

---

## /transactions/{id}/

### GET

transactions_read

API endpoint that allows transactions to be viewed or edited.

#### Responses

**200**



### PUT

transactions_update

API endpoint that allows transactions to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### PATCH

transactions_partial_update

API endpoint that allows transactions to be viewed or edited.

#### Parameters

- `data` (body): No description provided

#### Responses

**200**



### DELETE

transactions_delete

API endpoint that allows transactions to be viewed or edited.

#### Responses

**204**



### PARAMETERS

---

## /transactions/{transaction_id}/modify/

### POST

transactions_modify_create

Modify a specific transaction

#### Parameters

- `data` (body): No description provided

#### Responses

**200**

Transaction updated successfully

**404**

Transaction not found

### PARAMETERS

---

