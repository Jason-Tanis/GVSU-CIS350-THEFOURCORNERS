# Degree Dollars — The Four Corners 

![DegreeDollarsLogo](https://github.com/user-attachments/assets/e5210f21-5eef-44f1-845b-a035d83ab7d8)

Degree Dollars is a desktop budgeting application designed for college students to better manage their money. Built with BeeWare’s Toga framework and a MySQL backend, the app allows users to plan monthly budgets, record real-time income and expenses, and visualize their financial activity. It also features a student loan planner that calculates either the required monthly payment or the time needed to pay off a loan. With student-friendly UI design and modular features, Degree Dollars is supported on both macOS and Windows.

---

## Team Members and Roles

- [**Jason Tanis**](https://github.com/Jason-Tanis/CIS350-HW2-Tanis.git)  
  _Project Manager, Python Developer_

- [**Sam Bergman**](https://github.com/bergmasa/CIS350-HW2-Bergman.git)  
  _Python Developer_

- [**Tony Choummanivong**](https://github.com/TonyCyber6/CIS350-HW2--Choummanivong-.git)  
  _Python Developer, Software Tester_

- [**Kelsey Tedford**](https://github.com/kelseytedford/CIS350-HW2-Tedford)  
  _Prototype Developer, Python Developer, Database Manager_

---

## Prerequisites

To run Degree Dollars locally, ensure you have the following installed:

- Python 3.10 or higher
- MySQL Server (running on localhost)
- pip for managing Python packages
- Required Python packages:
  - `toga`
  - `mysql-connector-python`
  - `httpx`
  - `briefcase`

## Installation/Run Instructions

Open your terminal and follow the directions below.

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Jason-Tanis/GVSU-CIS350-THEFOURCORNERS.git
   cd GVSU-CIS350-THEFOURCORNERS/src/degree_dollars
   ```

2. **Install Dependencies**

   Make sure Python 3.10+ is installed. Then run:

   ```bash
   pip install toga mysql-connector-python httpx briefcase
   ```

3. **Start MySQL Server**

   Ensure your MySQL server is running locally with the following credentials:

   - **Host**: `localhost`
   - **Port**: `3306`
   - **User**: `root`
   - **Password**: `DegreeDollars350!`

4. **Package the App**

   ```bash
   briefcase create
   briefcase build
   ```

5. **Run the App**

   ```bash
   briefcase run

The app will create the required database (`DegreeDollars`) and all necessary tables on the first launch. On all subsequent runs, you need not run `briefcase create` and `briefcase build` again. Simply ensure you are in the directory `GVSU-CIS350-THEFOURCORNERS/src/degree_dollars` and execute the command `briefcase run`.

> **Note:** If you're new to MySQL or encounter connection issues, ensure the server is running and accessible via your configured credentials.

## Use Instructions
### Signing Up/Logging In

<p align="center">
  <img src="https://github.com/user-attachments/assets/17539eb7-ff2e-4432-aa56-a36483642b3b" width="250"/>
  <img src="https://github.com/user-attachments/assets/02ffae07-919d-46fd-9c5c-f9d65e0d11c9" width="250"/>
  <img src="https://github.com/user-attachments/assets/ab94c827-2de9-45da-bb15-cf44ce0c5133" width="250"/>
</p>


Upon opening the app, users will be prompted to either sign up or log in. New users must complete all fields on the sign-up screen. Once created, account credentials are stored in the MySQL database and can be used to log in to the app in the future.

### Account Management

<p align="center">
  <img src="https://github.com/user-attachments/assets/0f5da08b-2d54-4e92-825a-ec7e916615bf" width="250"/>
  <img src="https://github.com/user-attachments/assets/1ab4ec00-a2a6-4525-9ccd-3195e1c658d5" width="250"/>
  <img src="https://github.com/user-attachments/assets/49dcffc6-f220-4368-9558-a80290d2a2c2" width="250"/>
</p>

In the Profile menu, users can:

- Log out, which returns them to the welcome screen

- Change their username or password, which updates the information in the database

> **Note:** Duplicate usernames and passwords are not allowed

### Create Monthly Budget

<p align="center">
  <img width="250" src="https://github.com/user-attachments/assets/52889688-6d5f-48e9-bebb-739e4995f377" />
  <img width="250" src="https://github.com/user-attachments/assets/430f9b61-acc7-4be8-bc72-2301ed6fbabc" />
  <img width="250" src="https://github.com/user-attachments/assets/a407fc6a-4525-425a-9f4d-b8a7ce1a58a5" />
</p>

On the Home screen:

- If no budgets exist yet, users can select Create New Budget

- Users must specify the month and year for the budget

- Each budget contains seven predefined sections:

  - Education, Housing/Utilities, Food, Transportation, Entertainment, Medical, Other

- Users can add unlimited custom subsections and amounts

After inputting budget information, click Save Budget to store the data in the MySQL database.

<p align="center">
  <img width="250" src="https://github.com/user-attachments/assets/643b31b5-ad39-4c55-97e0-ed2b44f4bac7" />
  <img width="250" src="https://github.com/user-attachments/assets/d0ec8b06-866b-40aa-8313-5d62ad1df857" />
  <img width="250" src="https://github.com/user-attachments/assets/654d7935-b5a4-4354-b553-85eb516cf83c" />
</p>

In the "Homescreen" page, if there is already one or more budgets create, the user can select the month that they would like to view. Here are two examples of what budgets can look like.

### Income & Expenses

While viewing a specific month's budget, the user can log financial activity by using the "Add Transaction" button. The user must:

- Choose whether it's Income or Expense

- Select the section, subsection, date, merchant, and amount

- Click Save Transaction to update the database and adjust the corresponding budget totals

### Transaction History

In the "Transaction History" page, the user will use the dropdown to select a budget month. Once selected:
- A scrollable list of non-clickable transaction summaries will appear, sorted by date (newest to oldest).
- Each summary will show the
  - Date
  - Subsection
  - Merchant
  - Amount
    - Displayed in green with a "+" sign for income
    - Displayed in red with a "-" sign for expenses

### Student Loan Planner

In the "Loan Planner" page, the user has access two tools:

1. Calculate Monthly Payment
   Input loan amount, annual interest rate, and duration (months).

2. Calculate Timeline
  Input loan amount, annual interest rate, and monthly payment.

> **Note:**
> - Handles 0% interest correctly
> - All calculations are local and not stored in the database


