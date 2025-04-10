# Degree Dollars — The Four Corners

Degree Dollars is a cross-platform budgeting application designed for college students to better manage their money. Built with BeeWare’s Toga framework and a MySQL backend, the app allows users to plan monthly budgets, record real-time income and expenses, and visualize their financial activity. It also features a student loan planner that calculates either the required monthly payment or the time needed to pay off a loan. With student-friendly UI design and modular features, Degree Dollars supports all major platforms — desktop, mobile, and web.

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

## Run Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Jason-Tanis/GVSU-CIS350-THEFOURCORNERS.git
   cd GVSU-CIS350-THEFOURCORNERS
   ```

2. **Install Dependencies**

   Make sure Python 3.10+ is installed. Then run:

   ```bash
   pip install toga mysql-connector-python httpx
   ```

3. **Start MySQL Server**

   Ensure your MySQL server is running locally with the following credentials:

   - **Host**: `localhost`
   - **Port**: `3306`
   - **User**: `root`
   - **Password**: `DegreeDollars350!`

4. **Run the App**

   ```bash
   python src/degree_dollars/app.py
   ```

   The app will create the required database (`DegreeDollars`) and all necessary tables on first launch.

> **Note:** If you're new to MySQL or encounter connection issues, ensure the server is running and accessible via your configured credentials.

