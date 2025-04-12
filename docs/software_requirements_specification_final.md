# Overview

This document outlines the Software Requirements Specification (SRS) for Degree Dollars, a budgeting application designed specifically for college students. The app will have features that allow users to track and manage their finances throughout their time in school. Users will be able to create monthly budgets, add/subtract income and expenses from their saved budgets, review their transaction history, and plan student loan payments. This document details the functional and non-functional requirements neccessary for the development and implementation of the application.

# Functional Requirements
1. Create New Budget
    1. CBF1: The "Create New Budget" menu (accessible via the "Home" screen) shall contain seven (7) predefined sections: "Education", "Housing/Utilities", "Food", "Transportation", "Entertainment", "Medical", and "Other".
    2. CBF2: In the "Create New Budget" menu, the user shall be able to add infinitely many subsections to each predefined section.
    3. CBF3: The "Create New Budget" menu shall include two (2) input fields in which the user will specify the month and year for the budget (e.g., April 2025).
    4. CBF4: The user-entered budget information shall be added to the "Budgets" table in the MySQL database when the "Save Budget" button is pressed (one row for each subsection).
    5. CBF5: After a budget is saved, its name (e.g., "April 2025") shall be added to a dropdown menu on the "Home" screen from which the user can select a saved budget to view in a new screen.

2. Income/Expense
    1. IEF1: The "Income/Expense" feature shall be accessible via an "Income/Expense" button on the viewing screen for a previously saved budget
    2. IEF2: The "Income/Expense" button shall open a new window named "Add Transaction" (separate from the main window) when pressed.
    3. IEF3: The "Add Transaction" window shall contain the following input fields: "Income or Expense", "Section", "Subsection", "Month", "Day", "Year", "Amount", and "Merchant".
    4. IEF4: When the user presses the "Save Transaction" button in the "Add Transaction" window, a summary of their input shall be added to the "Transactions" table in the MySQL database (one row per transaction).
    5. IEF5: When the user presses the "Save Transaction" button in the "Add Transaction" window, the amount previously saved for the selected subsection shall be updated in the MySQL "Budgets" table accordingly.

3. History
    1. HF1: The "History" screen shall contain a dropdown menu identical to that of the "Home" screen from which the user can select a previously saved budget to view the transaction history for.
    2. HF2: After a budget is selected from the dropdown menu, a new screen shall open displaying a single column of non-clickable summaries of each transaction saved for the budget.
    3. HF3: The following information shall be displayed in each transaction summary: month and day, the subsection to which the transaction was applied, merchant, and amount (positive for income and negative for expenses).
    4. HF4: The subsections for each transaction shall be queried from the MySQL "Budgets" table while the remaining transaction information shall be queried from the "Transactions" table.
    5. HF5: The history viewing screen shall include a "Back to Home" button at the bottom of the transaction list that redirects the user to the "Home" screen (i.e., the screen containing the "Create New Budget" button).

4. Loan Planner
    1. LPF1: The "Loan Planner" screen shall contain two buttons: "Calculate Monthly Payment" and "Calculate Timeline".
    2. LPF2: If the "Calculate Monthly Payment" button is selected, a new screen shall open containing the following input fields: "Principle", "Annual Interest Rate (% APR)", and "Months to pay off".
    3. LPF3: The Loan Planner shall perform the computation "(Principle*I((1+I)^months))/(((1+I)^months)-1)" with the user-provided values when the "Compute!" button on the "Calculate Monthly Payment" screen is pressed (where I is the quotient "APR/12/100").
    4. LPF4: If the "Calculate Timeline" button is selected, a new screen shall open containing the following input fields: "Principle", "Interest Rate (%)", and "Amount of monthly payment".
    5. LPF5: The Loan Planner shall perform the computation "(log(Amt/(Amt-(Principle*I)))/(log(1+I))" with the user-provided values when the "Compute!" button on the "Calculate Timeline" screen is pressed (where Amt is the amount of monthly payment and I is the quotient "APR/12/100").

5. Profile
    1. ACCF1: When creating a new account via the "Sign Up" feature, the user shall provide their first and last name, username, and password.
    2. ACCF2: When a new account is created, it shall be added as a row to the "Profile" table in the MySQL database.
    3. ACCF3: When logging into an existing account via the "Log In" feature, the user shall provide their username and password.
    4. ACCF4: From the "Profile" screen, the user shall be able to change their username and/or password (the MySQL "Profile" table shall be updated accordingly).
    5. ACCF5: The "Profile" screen shall include a "Log Out" button that sets the currently active username, password, and client ID (the primary key of the MySQL "Profile" table) to "None" and redirects the user to the app's opening screen.

# Non-Functional Requirements
1. Create New Budget
    1. CBNF1: A user shall not have the ability to save more than one budget for the same month (e.g., two budgets for April 2025).
    2. CBNF2: If a user does does not provide any input to the "Create New Budget" menu, no rows shall be added to the MySQL "Budgets" table when the user selects "Save Budget".
    3. CBNF3: If a user provides a dollar amount for a subsection but no subsection name, no row for the subsection shall be added to the MySQL "Budgets" table when the user selects "Save Budget".
    4. CBNF4: If a user provides a name for a subsection but no dollar amount, a row for the subsection shall be added to the MySQL "Budgets" table when the user selects "Save Budget" with the default dollar amount $0.00.
    5. CBNF5: All budget subsections created by a user shall be saved to the MySQL "Budgets" table under their unique client ID (so they cannot be impacted by other users' activity).
  
2. Income/Expense
    1. IENF1: A user shall not be able to open more than one "Add Transaction" window at once.
    2. IENF2: Transactions saved by a user shall be saved to the MySQL "Transactions" table under their unique client ID (similarly to how budget subsections are saved).
    3. IENF3: The dialog message "Invalid date" shall appear if a user attempts to save a transaction with a non-real date (e.g., 02/29/2025; 02/30/2025; 04/31/2025) (such a transaction will not be saved to the MySQL database).
    4. IENF4: The dialog message "Please enter a non-zero dollar amount" shall appear if a user attempts to save a transaction of $0.00 (such a transaction will not be saved to the MySQL database).
    5. IENF5: The dialog message "Please enter a merchant name" shall appear if a user attempts to save a transaction without providing a merchant (such a transaction will not be saved to the MySQL database). 

3. History
    1. HNF1: None of a user's transactions shall under any circumstances be deleted from the MySQL "Transactions" table.
    2. HNF2: The dates of the transactions from the selected month shall be displayed as the first three letters of the month followed by a number representing the day.
    3. HNF3: The transaction summaries shall be displayed in descending order by date (i.e., the most recent transaction shall appear at the top of the list).
    4. HNF4: The dollar amounts for transactions of type "Income" shall appear as green numbers preceded by a "+" sign.
    5. HNF5: The dollar amounts for transactions of type "Expense" shall appear as red numbers preceded by a "-" sign.

4. Loan Planner
    1. LPNF1: If the interest rate provided to "Calculate Monthly Payment" is zero (0), the monthly payment shall simply be computed as "Principle/months".
    2. LPNF2: If the interest rate provided to "Calculate Timeline" is zero (0), the number of months to pay off the loan shall simply be computed as "Principle/Amt" (where Amt is the amount of monthly payment).
    3. LPNF3: In "Calculate Timeline", if the product between Principle and the monthly interest rate (i.e., the quotient "APR/12/100") is greater than or equal to the provided monthly payment amount, the message "Your plan is not recommended: try a larger monthly payment" shall be displayed in the results screen.
    4. LPNF4: The input fields for "Principle", "Months to pay off" and "Amount of monthly payment" shall not accept numbers less than or equal to zero (0).
    5. LPNF5: The input fields for interest rate shall not accept negative numbers, but zero (0) will be permitted.
    6. LPNF6: The Loan Planner feature shall not interact with the MySQL database.

5. Profile
    1. ACCNF1: One user shall not be allowed to have the same username as another user.
    2. ACCNF2: One user shall not be allowed to have the same password as another user.
    3. ACCNF3: If a user attempts to sign up without providing text to all five input fields, the dialog message "Please complete all fields" shall appear (the sign up will be prevented).
    4. ACCNF4: If a user attempts to sign up and the fields "Password" and "Confirm Password" do not contain identical, non-empty text, the dialog message "Passwords do not match" shall appear (the sign up will be prevented).
    5. ACCNF5: If a user attempts to log in with a username and/or password that do not exist in the MySQL "Profile" table, the dialog message "Invalid username or password" shall appear (the log in will be prevented).
