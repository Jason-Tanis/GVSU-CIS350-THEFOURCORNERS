# Overview

This document outlines the Software Requirements Specification (SRS) for Degree Dollars, a budgeting application. The system will have features that allow students in college to manage their finances throughout their school years. Users will be able to create and track monthly budgets, add/subtract income and expenses (respectively), review their transaction history, and plan student loan payments. This document details the functional and non-functional requirements neccessary for the development and implementation of the application.

# Functional Requirements
1. Create New Budget
    1. CBF1: The "Create New Budget" menu shall contain five (5) predefined categories: "Education", "Housing/Utilities", "Food", "Transportation", and "Entertainment".
    2. CBF2: In the "Create New Budget" menu, the user shall be able to add infinitely many subcategories to each predefined category. 
    3. CBF3: The user-entered budget information shall be stored in a SQL database specific to the current active user when the "Save Budget" button is selected.

2. Add Income/Expense
    1. IEF1: The "Add Income/Expense" button shall exist inside the window for viewing a previously saved budget.
    2. IEF2: The feature shall have the following input fields: "Income or Expense", "Date", "Amount", "Section (and subsection)", and "Merchant".
    3. IEF3: When the user completes recording their transaction, a summary of their input shall be saved to the database.
    4. IEF4: When the user completes recording their transaction, the corresponding budget shall be updated in the databased.

3. Transaction History
    1. THF1: The "Transaction History" screen shall display a column of non-clickable summary boxes for each individual transaction made by the user.
    2. THF2: The month of the transaction shall be displayed as the first three (3) letters of the month (e.g., "JAN", "FEB", "MAR").

4. Loan Payment Planner
    1. LPF1: The feature shall receive the total loan amount, the interest rate, and either the user's planned monthly payment amount or their planned time frame (in months) to pay the loan in full as input.
    2. LPF2: If the user did not enter their planned monthly payment amount, the number of months to pay the loan in full shall be computed and displayed.
    3. LPF3: If the user did not enter their planned time frame, the amount to pay per month shall be computed and displayed.

5. Login
    1. ACCF1: On the opening screen, the user shall have the option to either create a new account, or log in to an existing account.
    2. ACCF2: Once a new account is created, the application shall allow the user to log in using the new account in the future.
    3. ACCF3: The "Log out" button on the "Profile" screen shall redirect the user to the opening screen when clicked.

# Non-Functional Requirements
1. General (i.e., the app as a whole)
    1. GNF1: Database interactions (e.g., logging in; saving a budget) shall take no longer than 10 seconds.
    2. GNF2: If a screen in the application is either broken or under development, the user shall receive an error message and be allowed to return to the previous screen.
    3. GNF3: The color scheme of the app shall appear similarly across different platforms.
    4. GNF4: Button labels shall contain a maximum of two words.

2. Create New Budget
    1. CBNF1: The application shall be optimized for the latest tech stack to allow for a greater amount of storage space.
  
4. Add Income/Expense
    1. IENF1: The "Date" input field shall be formatted in such a way that the values it receives can be accurately represented across various platforms (e.g., Android, iOS, Windows, Mac).

5. Transaction History
    1. THNF1: All of a user's transactions (i.e., income/expenses) shall be preserved in the database (i.e., they shall never be deleted).

6. Loan Payment Planner
    1. LPNF1: The loan payment planner feature shall not interact with the database.
    2. LPNF2: Computation shall take no longer than three (3) seconds to complete.

7. Login
    1. ACCNF1: One user shall not be able to deliberately sign in to a separate user's account.
    2. ACCNF2: One user shall not be able to unintentionally access a separate user's account.
    3. ACCNF3: The user account database shall not allow there to be more than one account with the same username.
    4. ACCNF4: The user account database shall be remote (i.e., it shall not included in a local download of the application).
    5. ACCNF5: The user account database shall allow users to access their budget information via multiple devices (e.g., an iPhone and a Windows computer).
    6. ACCNF6: User passwords shall be hashed when stored in the database.
