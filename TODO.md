# TODO List

## 1. Improve Transaction List View
- [X] Redesign the transaction list component to match the review section's layout
- [X] Implement filters for the transaction list (e.g., by date range, description, amount)
- [X] Add sorting functionality for each column in the transaction list
- [X] Implement pagination for the transaction list
- [X] Implement server-side pagination

## 2. API Documentation
- [X] Set up a tool for API documentation (e.g., Swagger/OpenAPI)
- [ ] Document all existing API endpoints
- [ ] Include request/response examples for each endpoint
- [ ] Add authentication details to the API documentation
- [ ] Add API documentation links to Frontend

## 3. Expand Testing
- [ ] Set up a testing framework for the React frontend (e.g., Jest, React Testing Library)
- [ ] Write unit tests for key React components
- [ ] Expand Django unit tests for models and views
- [ ] Implement integration tests for critical user flows
- [ ] Set up CI/CD pipeline for automated testing

## 4. Security Enhancements
- [ ] Implement comprehensive input validation on both frontend and backend
- [ ] Ensure proper CSRF protection is in place for all forms
- [ ] Review and enhance secure data storage practices
- [ ] Implement rate limiting for API endpoints
- [ ] Conduct a security audit and address any findings

## 5. Theme Management in User Settings
- [ ] Create a user settings model to store user preferences including theme
- [ ] Implement a theme selection component in the user interface
- [ ] Create a theme switching mechanism in the frontend
- [ ] Ensure all components and styles respect the selected theme
- [ ] Persist theme selection in the database and apply it on user login