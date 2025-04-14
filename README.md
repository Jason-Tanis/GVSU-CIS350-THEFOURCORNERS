# Degree Dollars — The Four Corners 

![DegreeDollarsLogo](https://github.com/user-attachments/assets/e5210f21-5eef-44f1-845b-a035d83ab7d8)

Degree Dollars is a desktop budgeting application designed for college students to better manage their money. Built with BeeWare’s Toga framework and a MySQL backend, the app allows users to plan monthly budgets, record real-time income and expenses, and visualize their financial activity. It also features a student loan planner that calculates either the required monthly payment or the time needed to pay off a loan. With student-friendly UI design and modular features, Degree Dollars is supported on both macOS and Windows.

---

## Team Members and Roles

- [**Jason Tanis**](https://github.com/Jason-Tanis/CIS350-HW2-Tanis.git)  
  _Project Manager, Python Developer, Android Tester_

- [**Sam Bergman**](https://github.com/bergmasa/CIS350-HW2-Bergman.git)  
  _Python Developer_

- [**Tony Choummanivong**](https://github.com/TonyCyber6/CIS350-HW2--Choummanivong-.git)  
  _Python Developer, Unit Tester_

- [**Kelsey Tedford**](https://github.com/kelseytedford/CIS350-HW2-Tedford)  
  _Prototype Developer, Python Developer, Database Manager, iOS Tester_

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

![App Sign Up Screen](https://github.com/user-attachments/assets/48b90018-d927-4440-912a-32fe52fb3f19) ![App Log In Screen](https://github.com/user-attachments/assets/77121036-4846-47a6-bee2-e5dcb6b716c4)

Upon opening the app, you will be prompted to either sign up or log in. If you have not yet created an account with Degree Dollars, you will need to sign up, completing all fields on the sign up screen. Once you sign up, your account information will be stored in the MySQL database, and you can log in to your created account in the future.

### Changing your Account Credentials

![Change Username](https://github.com/user-attachments/assets/f411da78-fc5f-4f3e-99be-18fd0852880d) ![Change Password](https://github.com/user-attachments/assets/cc2426a1-58dc-41b3-ab6e-3cc8d2096f41)

In the "Profile" menu, you are provided the option to log out of your currently active account. Additionally, you can change your username and/or your password. Your account credentials will be updated in the MySQL database accordingly.
