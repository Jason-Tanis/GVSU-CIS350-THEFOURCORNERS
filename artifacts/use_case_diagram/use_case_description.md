## Use Case
Add Income/Expense

## Actors
User (initiator), MySQL Database

## Description

1. The User selects the "Add Income/Expense" button on the viewing screen for one of their monthly budgets.
2. The User indicates the following: whether they are adding income or an expense, the date of the transaction (day of month), the dollar amount, the section and subsection of the budget, and the merchant.
3. The details of the transaction are saved to the Transactions table in the MySQL database.
4. The budget in which the transaction was made is updated in the Budgets table in the MySQL database.

## Cross Ref.
Requirements IEF1, IEF2, IEF3, IEF4, IEF5, IENF1, IENF2, IENF3, IENF4, and IENF5

## Use-Cases
User must have created at least one budget; at least one budget must have been saved to MySQL database

## Link to Diagram
[Use-Case Diagram](https://github.com/Jason-Tanis/GVSU-CIS350-THEFOURCORNERS/blob/868092dde42a1db8584cc900c8d059f87b6c45a6/artifacts/use_case_diagram/Degree%20Dollars%20Use%20Case%20Diagram.pdf)
