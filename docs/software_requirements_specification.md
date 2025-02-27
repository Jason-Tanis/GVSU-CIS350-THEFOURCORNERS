# Overview

This document outlines the Software Requirements Specification (SRS) for Degree Dollars, a budgeting application. The system will have features that allow students in college to manage their finances throughout their school years. Users will be able to create and track monthly budgets, add/subtract income and expenses (respectively), review their transaction history, and plan student loan payments. This document details the functional and non-functional requirements neccessary for the development and implementation of the application.

# Functional Requirements
1. Create New Budget
    1. CBF1: The "Create New Budget" menu shall contain seven (7) predefined categories: "Education", "Housing/Utilities", "Food", "Transportation", "Medical", "Entertainment", and "Other".
    2. CBF2: In the "Create New Budget" menu, the user shall be able to add an unlimited number of additional subcategories to each predefined category. 
    3. CBF3: The user-entered budget information shall be stored in a SQL database specific to the current active user when the "Save Budget" button is selected.

2. Add Income/Expense
    1. IEF1: The "Add Income/Expense" button shall exist inside the window for viewing a previously saved budget.
    2. IEF2: The feature shall have the following input fields: "Income or Expense", "Date", "Amount", "Section (and subsection)", "Merchant".
    3. IEF3: When the user completes recording their transaction, a summary of their input shall be saved to their user-specific SQL database.

3. Transaction History
    1. THF1: The "Transaction History" screen shall display non-clickable summary boxes for each individual transaction made by the user.
    2. THF2: The month of the transaction shall be displayed as the first three (3) letters of the month (e.g., "JAN", "FEB", "MAR").

# Non-Functional Requirements
1. Create New Budget
    1. CBNF1: The user's local download of the application shall not contain the the SQL database of their saved budget information.
    2. CBNF2: One active user shall not be able to intentionally or unintentionally modify the saved budget information of another user.

2. Add Income/Expense
    1. IENF1: The "Date" input field shall be formatted in such a way that the values it receives can be accurately represented across various platforms (e.g., Android, iOS, Windows, Mac).

