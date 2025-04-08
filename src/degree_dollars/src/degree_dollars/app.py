"""
A budgeting application for undergraduate and graduate college students
"""

import toga
import os
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, RIGHT, LEFT, HIDDEN, VISIBLE
import mysql.connector
import datetime
from functools import partial
import math
import asyncio

# MySQL Connection Settings
config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "DegreeDollars350!"
}
MYSQL_DATABASE = "DegreeDollars"


def create_database(app):
    """Creates the MySQL database and necessary tables if they don’t exist."""
    # Connect to MySQL Server
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    try:
        # Create Database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        cursor.execute(f"USE {MYSQL_DATABASE}")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile (
        client_id INTEGER PRIMARY KEY AUTO_INCREMENT,
        password VARCHAR(255) NOT NULL, -- hash the password before storing in db
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        username VARCHAR(50) NOT NULL UNIQUE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
        budget_id INTEGER PRIMARY KEY AUTO_INCREMENT,
        client_id INTEGER,
        section CHAR(50),
        subsection CHAR(50),
        budget_total NUMERIC,
        month INTEGER, -- 1 through 12 will be stored
        year INTEGER,
        
        FOREIGN KEY (client_id)
            REFERENCES profile(client_id)
            ON DELETE CASCADE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTO_INCREMENT,
        client_id INTEGER,
        budget_id INTEGER,
        date DATE,
        amount NUMERIC,
        merchant CHAR(50),
        expense BOOL,

        FOREIGN KEY (client_id)
            REFERENCES profile(client_id)
            ON DELETE CASCADE,

        FOREIGN KEY (budget_id)
            REFERENCES budgets(budget_id)
            ON DELETE CASCADE
        )
        ''')

        conn.commit()
        print("Database and tables created successfully!")
        
    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
      
    finally:
        cursor.close()
        conn.close()

class DegreeDollars(toga.App):
    def startup(self): #Define the app's behavior when it is initially opened
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        
        # create database
        create_database(self)
        
        self.main_window = toga.MainWindow(title=self.formal_name) #Window in which box is displayed
        self.startscreen()

    async def homescreen(self, widget): #Open the Home Screen of the app

        #Create boxes for each navigation bar tab (currently, they are all empty boxes except for home content)
        profile = self.empty_box()
        loan    = self.empty_box()
        history = self.empty_box()
        home    = self.empty_box()

        #Profile
        #Connect to database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"USE {MYSQL_DATABASE}")
        cursor.execute('''
            SELECT * FROM profile WHERE username = %s AND password = %s
            ''',
                       (self.username, self.password))
                       
        result = cursor.fetchone()
        
        self.first_name = result[2]
        self.last_name = result[3]
            
        conn.close()
    
        #Greeting
        greeting_container = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, background_color="white", padding=20, width=500))

        greeting_label = toga.Label(
        f"Hello, {self.first_name} {self.last_name[0]}.! Welcome to your Profile!",
        style=Pack(font_size=18, font_weight="bold", padding=(20, 0), background_color="white", text_align=CENTER)
        )
        greeting_container.add(greeting_label)
        
        #Change username
        change_username_container = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, background_color="white", padding=20, width=500))
        username_label = toga.Button(
            "Change Username",
            on_press=self.change_username,
            style=Pack(background_color="#FFFFFF", alignment=CENTER, padding=(35,0,0), width=500, height=40))
        change_username_container.add(username_label)
        change_username_container.add(toga.Box(style=Pack(height=40)))
        
        #Change password
        change_password_container = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, background_color="white", padding=20, width=500))
        password_label = toga.Button(
            "Change Password",
            on_press=self.change_password,
            style=Pack(background_color="#FFFFFF", alignment=CENTER, padding=(35,0,0), width=500, height=40))
        change_password_container.add(password_label)
        change_password_container.add(toga.Box(style=Pack(height=40)))
        
        profile.add(greeting_container, change_username_container, change_password_container)


        # Homescreen
        # Create New Budget Button
        create_budget_button = toga.Button(
            "Create New Budget",
            on_press=self.create_budget_view,
            style=Pack(background_color="#62C54C", padding=(35, 0, 0),
            width=300, height=55, font_weight="bold", font_size=18,color="#000000")
        )
        home.add(create_budget_button)

        #Create navigation bar as an OptionContainer
        navbar = toga.OptionContainer(
                style = Pack(background_color = ("#62C54C")),
                content = [
                    toga.OptionItem("Profile", profile),
                    toga.OptionItem("Home", home),
                    toga.OptionItem("Loan Planner", loan),
                    toga.OptionItem("History", history)
                ]
        )
        
        self.history_box = history

        #Make "Home" the currently open tab
        navbar.current_tab = "Home"
        
        # Connect to MySQL Server
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"USE `{MYSQL_DATABASE}`")
        
        #Find client_id
        cursor.execute('''
        SELECT client_id FROM profile WHERE username = %s AND password = %s
        ''', (self.username, self.password))

        result = cursor.fetchone()
        
        if result:
            self.client_id = result[0]
            
        else:
            print("Error: client_id not found")
            return

        # Get all of the user's budgets
        cursor.execute('''
        SELECT DISTINCT month, year FROM budgets WHERE client_id = %s ORDER BY year DESC, month DESC
        ''', (self.client_id,))
        all_budgets = cursor.fetchall()

        #List for displaying dropdown menu options
        dropdown_options = []

        #List of month names
        month_names = ["January", "February", "March", "April", "May", "June", 
                       "July", "August", "September", "October", "November", "December"]
        
        #If the user has saved at least one budget,
        #create and add a dropdown menu to select one of the saved budgets to view/edit
        #(these widgets will appear on the Home screen)
        if all_budgets:
            for budget in all_budgets:
                month_name = month_names[budget[0] - 1]
                year = budget[1]
                budget_title = f"{month_name} {year}"
                tmp_dictionary = {"name": budget_title, "data": budget}
                dropdown_options.append(tmp_dictionary)
            selectbudget_label = toga.Label(
                "View/Edit Budget",
                style = Pack(
                    font_size = 14,
                    font_weight = "bold",
                    color = "#000000",
                    background_color = "#C0E4B8",
                    text_align = CENTER,
                    padding = (35, 0, 0)
                )
            )
            budget_dropdown = toga.Selection(
                items = dropdown_options, 
                accessor = "name",
                style = Pack(
                    width = 300,
                    padding = (15, 0, 0)
                ),
                on_change = self.view_edit_budget
            )
            home.add(selectbudget_label, budget_dropdown)
        else:
            all_budgets = []
            selectbudget_label = toga.Label(
                "No saved budgets found. Create a new one!",
                style = Pack(
                    font_size = 12,
                    color = "#000000",
                    background_color = "#C0E4B8",
                    text_align = CENTER,
                    padding = (35, 0, 0)
                )
            )
            home.add(selectbudget_label)

        #If the user has saved at least one budget,
        #create and add a dropdown menu to select one of the saved months to view transaction history for
        #(these widgets will appear on the History screen) 
        if all_budgets:
            history_label = toga.Label(
                "View Transaction History for:",
                style = Pack(
                    font_size = 14,
                    font_weight = "bold",
                    color = "#000000",
                    background_color = "#C0E4B8",
                    padding = (35, 0, 0),
                    text_align = CENTER
                )
            )
            history_dropdown = toga.Selection(
                items = dropdown_options, 
                accessor = "name",
                style = Pack(
                    width = 300,
                    padding = (15, 0, 0)
                ),
                on_change = self.see_my_history
            )
            history.add(history_label, history_dropdown)
        else:
            history_label = toga.Label(
                "No saved budgets found. Create a new one!",
                style = Pack(
                    font_size = 12,
                    color = "#000000",
                    background_color = "#C0E4B8",
                    text_align = CENTER,
                    padding = (35, 0, 0)
                )
            )
            history.add(history_label)

        # conn.close()
        # Loan Planner
        buttons_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        
        #Titles
        loan_planner_label = toga.Label("Loan Payment Planner", style=Pack(font_size=18, font_weight="bold", padding=10,color="#000000"))
        
        info_label = toga.Label("Choose one of the options below:", style=Pack(font_size=12, font_weight="bold", padding=10,color="#000000", text_align=CENTER))

        info_label_month = toga.Label("(Must know the number of monthly payments you plan to make)", style=Pack(font_size=12, padding=10,color="#000000", text_align=CENTER))
        
        info_label_payment = toga.Label("(Must know the monthly payment amount (in dollars) you plan to make)", style=Pack(font_size=12, padding=10,color="#000000", text_align=CENTER))
        
        calculate_payment_button = toga.Button(
            "Calculate Monthly Payment",
            on_press=self.calculate_payment,
            style=Pack(font_size=18, width=400, height=40, padding=10,color="#000000")
        )
        calculate_timeline_button = toga.Button(
            "Calculate Timeline",
            on_press=self.calculate_timeline,
            style=Pack(font_size=18, width=400, height=40, padding=10,color="#000000")
        )
        buttons_box.add(calculate_payment_button, info_label_month, calculate_timeline_button, info_label_payment)
        loan.add(loan_planner_label, info_label, buttons_box)

        #Display the homescreen contents
        self.main_window.content = navbar
        self.main_window.show()


    async def calculate_payment(self, widget): # Calculate the payment required for the timeline
        parent_box = widget.parent # buttons box
        grandparent_box = parent_box.parent # loan
        grandparent_box.clear()
        
        #Titles
        title = toga.Label("Compute Monthly Payment", style=Pack(font_size=18, font_weight="bold", padding=10,color="#000000", text_align=CENTER))
        
        info_label = toga.Label("Please enter the following information:", style=Pack(font_size=12, font_weight="bold", padding=10,color="#000000", text_align=CENTER))

        payment_calculator_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        
        #Principle
        principle_box = toga.Box(style=Pack(padding=(5, 5), direction=ROW, alignment=LEFT))
        principle_label = toga.Label("Principle:", style=Pack(font_size=12, text_align=LEFT,color="#000000"))
        principle_input = toga.NumberInput(min=0.01, value=1.00, step=0.01, style=Pack(width=100, padding=(5, 5)))
        principle_box.add(principle_label, principle_input)
        
        #Interest Rate
        interest_box = toga.Box(style=Pack(padding=(5, 5), direction=ROW, alignment=LEFT))
        interest_label = toga.Label("Annual Interest Rate (% APR):", style=Pack(font_size=12, text_align=LEFT,color="#000000"))
        interest_input = toga.NumberInput(min=0.00, value=0.00, step=0.01, style=Pack(width=100, padding=(5, 5)))
        interest_box.add(interest_label, interest_input)
        
        #Selected Months
        timeline_box = toga.Box(style=Pack(padding=(5, 5), direction=ROW, alignment=LEFT))
        timeline_label = toga.Label("Months to pay off:", style=Pack(font_size=12, text_align=LEFT,color="#000000"))
        timeline_input = toga.NumberInput(min=1.00, value=1.00, step=1, style=Pack(width=100, padding=(5, 5)))
        timeline_box.add(timeline_label, timeline_input)
        
        #Save values for computation
        self.principle = principle_input
        self.interest = interest_input
        self.months = timeline_input
        
        calculate_payment_button_final = toga.Button(
            "Compute!",
            on_press=partial(self.calculate_payment_math),
            style=Pack(font_size=18, width=400, height=40, padding=10, color="#000000")
        )
        
        #Back to Homescreen
        back_btn = toga.Button("Back to Home", on_press=self.homescreen, style=Pack(padding=10, width=150))
        
        payment_calculator_box.add(title, info_label, principle_box, interest_box, timeline_box, calculate_payment_button_final, back_btn)
        
        print(payment_calculator_box)
        grandparent_box.add(payment_calculator_box)
    
    async def calculate_payment_math(self, widget):
        parent_box = widget.parent # buttons box
        grandparent_box = parent_box.parent # loan
        grandparent_box.clear()
        
        self.principle = self.principle.value
        self.interest = self.interest.value
        self.months = self.months.value
    
        #Result box
        results_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER,background_color="#62C54C", padding=20, width=350))
        
        #Header
        results_title = toga.Label("Results", style=Pack(font_size=24, text_align=LEFT, font_weight="bold", padding=(0,0,10)))
        
        #Inner box
        info_container = toga.Box(style=Pack(direction=COLUMN, background_color="white", padding=20, width=325))
        
        #Principle
        principle_container = toga.Box(style=Pack(direction=ROW, width = 325))
        principle_text = toga.Label("Total loan amount:", style=Pack(font_size=16, flex=1, text_align=LEFT))
        principle_amount = toga.Label(f"${self.principle}", style=Pack(font_size=16, text_align=RIGHT))
        principle_container.add(principle_text, principle_amount)
        
        
        #Interest
        interest_container = toga.Box(style=Pack(direction=ROW, width = 325))
        interest_text = toga.Label(f"Interest rate:", style=Pack(font_size=16, flex=1, text_align=LEFT))
        interest_amount = toga.Label(f"{self.interest}%", style=Pack(font_size=16, text_align=RIGHT))
        interest_container.add(interest_text, interest_amount)

        #Month
        month_container = toga.Box(style=Pack(direction=ROW, width = 325))
        month_text = toga.Label(f"Planned duration:", style=Pack(font_size=16, flex=1, text_align=LEFT))
        month_amount = toga.Label(f"{self.months} months", style=Pack(font_size=16, text_align=RIGHT))
        month_container.add(month_text, month_amount)

        monthly_interest_rate = self.interest / 12 / 100
        if monthly_interest_rate == 0:
            recommendation = self.principle / self.months
        else:
            recommendation = (self.principle * monthly_interest_rate * (1 + monthly_interest_rate)**self.months) / ((1 + monthly_interest_rate)**self.months - 1)
            
        rec_container = toga.Box(style=Pack(direction=COLUMN, background_color="white", padding=20, width=325))
        recommendation_label = toga.Label("Recommended monthly payment:", style=Pack(font_size=16, text_align=CENTER))
        recommendation_output = toga.Label(f"${recommendation:.2f} per month", style=Pack(font_size=24, text_align=CENTER))
        rec_container.add(recommendation_label, recommendation_output)

        info_container.add(principle_container, interest_container, month_container)

        results_box.add(results_title, info_container, rec_container)
        
        #Back to Homescreen
        back_btn = toga.Button("Back to Home", on_press=self.homescreen, style=Pack(padding=10, width=150))
        
        grandparent_box.add(results_box, back_btn)

        
    async def calculate_timeline(self, widget): # Calculate the timeline from data
        parent_box = widget.parent # buttons box
        grandparent_box = parent_box.parent # loan
        grandparent_box.clear()
        
        #Principle
        principle_box = toga.Box(style=Pack(padding=(5, 5), direction=ROW, alignment=LEFT))
        principle_label = toga.Label("Principle:", style=Pack(font_size=12, text_align=LEFT,color="#000000"))
        principle_input = toga.NumberInput(min=0.01, value=1.00, step=0.01, style=Pack(width=100, padding=(5, 5)))
        principle_box.add(principle_label, principle_input)
        
        #Interest Rate
        interest_box = toga.Box(style=Pack(padding=(5, 5), direction=ROW, alignment=LEFT))
        interest_label = toga.Label("Interest Rate (%):", style=Pack(font_size=12, text_align=LEFT,color="#000000"))
        interest_input = toga.NumberInput(min=0.00, value=0.00, step=0.01, style=Pack(width=100, padding=(5, 5)))
        interest_box.add(interest_label, interest_input)
        
        #Selected Payment
        timeline_calculator_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        payment_box = toga.Box(style=Pack(padding=(5, 5), direction=ROW, alignment=LEFT))
        payment_label = toga.Label("Amount of monthly payment:", style=Pack(font_size=12, text_align=LEFT))
        payment_input = toga.NumberInput(min=0.01, value=1.00, step=0.01, style=Pack(width=100, padding=(5, 5)))
        payment_box.add(payment_label, payment_input)
        
        #Save values for computation
        self.principle = principle_input
        self.interest = interest_input
        self.monthly_payment = payment_input
        
        calculate_timeline_button_final = toga.Button(
            "Compute!",
            on_press=partial(self.calculate_timeline_math),
            style=Pack(font_size=18, width=400, height=40, padding=10)
        )
                
        #Back to Homescreen
        back_btn = toga.Button("Back to Home", on_press=self.homescreen, style=Pack(padding=10, width=150))
        
        timeline_calculator_box.add(principle_box, interest_box, payment_box, calculate_timeline_button_final, back_btn)
        
        grandparent_box.add(timeline_calculator_box)

    async def calculate_timeline_math(self, widget):
        parent_box = widget.parent # buttons box
        grandparent_box = parent_box.parent # loan
        grandparent_box.clear()
        
        self.principle = self.principle.value
        self.interest = self.interest.value
        self.monthly_payment = self.monthly_payment.value
        
        #Result box
        results_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER,background_color="#62C54C", padding=20, width=350))
        
        #Header
        results_title = toga.Label("Results", style=Pack(font_size=24, text_align=LEFT, font_weight="bold", padding=(0,0,10)))
        
        #Inner box
        info_container = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, background_color="white", padding=20, width=325))
        
        info_loan = toga.Label(f"Total loan amount:     ${self.principle}", style=Pack(font_size=16, text_align=CENTER))
        
        info_interest = toga.Label(f"Interest rate:     {self.interest}%", style=Pack(font_size=16, text_align=CENTER))
        
        info_months = toga.Label(f"Planned monthly payment:     ${self.monthly_payment}", style=Pack(font_size=16, text_align=CENTER))
        
        info_container.add(info_loan, info_interest, info_months)
        
        #Recommended Payment Section
        monthly_interest_rate = self.interest / 12 / 100
        if monthly_interest_rate == 0:
            recommendation = self.principle / self.monthly_payment
        elif self.principle * monthly_interest_rate >= self.monthly_payment:
            recommendation = -1
        else:
            recommendation = (math.log(self.monthly_payment / (self.monthly_payment - self.principle * monthly_interest_rate))) / (math.log(1 + monthly_interest_rate))
        
        rec_container = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, background_color="white", padding=20, width=325))
        
        if recommendation == -1:
            recommendation_label = toga.Label("Your plan is not recommended:", style=Pack(font_size=16, text_align=CENTER))
            recommendation_output = toga.Label(f"try a larger monthly payment", style=Pack(font_size=16, text_align=CENTER))
        else:
            recommendation_label = toga.Label("Recommended payment duration:", style=Pack(font_size=16, text_align=CENTER))
            recommendation_output = toga.Label(f"{recommendation:.0f} months", style=Pack(font_size=24, text_align=CENTER))
        
        rec_container.add(recommendation_label, recommendation_output)

        results_box.add(results_title, info_container, rec_container)
        
        #Back to Homescreen
        back_btn = toga.Button("Back to Home", on_press=self.homescreen, style=Pack(padding=10, width=150))
        
        grandparent_box.add(results_box, back_btn)


    async def create_budget_view(self, widget): #New viewing screen for creating new budget
        budget_box = self.empty_box()

        #Title
        title = toga.Label("Create New Budget", style=Pack(background_color="#C0E4B8", color="#000000", font_size=24, font_weight="bold", padding=(10, 0)))
        budget_box.add(title)

        #Add a box in which the user can specify the current month and year
        spacer = toga.Box(style=Pack(background_color="#C0E4B8", direction=COLUMN, padding=(0,10)))
        month_box = toga.Box(style=Pack(background_color="#C0E4B8", direction=ROW, alignment=CENTER))
        year_box = toga.Box(style=Pack(background_color="#C0E4B8", direction=ROW, alignment=CENTER))

        monthfield_label = toga.Label("Month", style=Pack(background_color="#C0E4B8", color="#000000", font_size=18, padding_left=10))
        yearfield_label = toga.Label("Year", style=Pack(background_color="#C0E4B8", color="#000000", font_size=18, padding_left=10))
        months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
        current_month_index = datetime.datetime.now().month - 1
        self.month_selection = toga.Selection(items=months, value=months[current_month_index], style=Pack(width=250))
        self.year_selection = toga.NumberInput(min=datetime.datetime.now().year, value=datetime.datetime.now().year, 
                                               step=1, style=Pack(width=100, padding=(5, 5)))
    
        month_box.add(monthfield_label, self.month_selection)
        year_box.add(yearfield_label, self.year_selection)
        spacer.add(month_box, year_box)
        budget_box.add(spacer)

        #Predefined sections
        sections = ["Education", "Housing/Utilities", "Food", "Transportation", "Entertainment",
                    "Medical", "Other"]
        for section in sections:
            section_box = self.create_budget_section(section)
            budget_box.add(section_box)

        #Save Budget Button
        save_button = toga.Button(
            "Save Budget",
            on_press=self.save_budget,
            style=Pack(
                background_color="#62C54C", 
                padding=(10, 0, 10), 
                width=150, 
                height=50, 
                font_weight="bold", 
                font_size=14,
                color="#000000"
            )
        )
        #Home button
        home_button = toga.Button(
            "Home",
            on_press=self.homescreen,
            style=Pack(
                background_color="#62C54C",
                padding=(0, 0, 10),
                width=150, 
                height=50, 
                font_weight="bold", 
                font_size=14, 
                color="#000000"
            )
        )
        budget_box.add(save_button, home_button)

        #For Scrolling
        scroll_container = toga.ScrollContainer(content=budget_box, horizontal=False, style=Pack(padding=10))
        
        self.main_window.content = scroll_container
        self.main_window.show()
        
    def create_budget_section(self, section):
        section_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # title
        section_label = toga.Label(section, style=Pack(font_size=20, font_weight="bold",color="#000000"))
        section_box.add(section_label)
        
        # default subsections
        for _ in range(2):
            subsection_box = self.create_budget_subsection()
            section_box.add(subsection_box)
            
        # add subsection button
        add_subsection_button = toga.Button("Add Subsection +", on_press=self.add_budget_subsection, style=Pack(padding=5, font_size=14,color="#000000")
                                            )
        section_box.add(add_subsection_button)
        
        return section_box
        
    # Helper function to create a budget subsection
    def create_budget_subsection(self):
        subsection_box = toga.Box(style=Pack(direction=ROW, padding=5, alignment=CENTER))

        # Subsection Name
        subsection_input = toga.TextInput(placeholder="Subsection", style=Pack(width=150, padding=(5, 5)))

        # Budget Amount
        amount_input = toga.NumberInput(min=0.00, value=0.00, step=0.01, style=Pack(width=100, padding=(5, 5)))

        # Remaining Budget Label
        remaining_label = toga.Label("$0.00 left", style=Pack(font_size=14, padding_left=10,color="#000000"))

        subsection_box.add(subsection_input)
        subsection_box.add(amount_input)
        subsection_box.add(remaining_label)

        return subsection_box

    async def add_budget_subsection(self, widget):
        parent_box = widget.parent
        parent_box.remove(widget) #Temporarily remove the "Add Subsection +" button
        new_subsection = self.create_budget_subsection()
        parent_box.add(new_subsection)
        parent_box.add(widget) #Re-insert the "Add Subsection +" button
        
    async def save_budget(self, widget):

        # Create database if one isn't already created
        create_database(self)
        
        # Connect to MySQL Server
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Get selected month and year
        self.month_names = ["January", "February", "March", "April", "May", "June", "July","August", "September", "October", "November", "December"]
        selected_month = self.month_selection.value
        selected_month_number = self.month_names.index(selected_month) + 1
        year = self.year_selection.value
        
        #Find client_id
        cursor.execute(f"USE {MYSQL_DATABASE}")
        cursor.execute('''
        SELECT client_id FROM profile WHERE username = %s AND password = %s
        ''', (self.username, self.password))

        result = cursor.fetchone()
        
        if result:
            self.client_id = result[0]
            
        else:
            print("Error: client_id not found")
            return

        #Display a dialog box if the user has already saved a budget for the same month and year
        cursor.execute('''
        SELECT month, year FROM budgets WHERE client_id = %s AND month = %s AND year = %s
        ''', (self.client_id, selected_month_number, year))
        result = cursor.fetchone()
        if result:
            invalid = toga.InfoDialog("Duplicate budget", f"You have already saved a budget for {selected_month} {year}")
            await self.main_window.dialog(invalid)
            return           

        #Current Budget
        cursor.execute('''
        SELECT budget_id FROM budgets WHERE client_id = %s AND year = %s AND month = %s
        ''', (self.client_id, year, selected_month_number))

        budget_we_on = cursor.fetchone()

        # Iterate through sections and save them
        for section in self.main_window.content.content.children[2:-2]:
            if isinstance(section, toga.Box):  # Ensure it's a section
                section_name = section.children[0]  # First child is the section label
                section_text = section_name.text

                for sub_box in section.children[1:-1]:  # Skip first (section label) and last (Add Subsection button)
                    if isinstance(sub_box, toga.Box) and sub_box.children[0].value != '':  # Ensure it's a subsection and exists

                        subsection_input = sub_box.children[0]  # First child: Subsection input
                        amount_input = sub_box.children[1]  # Second child: Amount input

                        subsection_name = subsection_input.value
                        amount = amount_input.value
                        
                        amount = amount_input.value if amount_input.value is not None else 0
                        
                        # Insert data into database
                        cursor.execute(f"USE `{MYSQL_DATABASE}`")
                        cursor.execute("INSERT INTO budgets (client_id, section, subsection, budget_total, month, year) "
                            "VALUES (%s, %s, %s, %s, %s, %s)",
                            (self.client_id, section_text, subsection_name, float(amount), selected_month_number, year)
                            )
        conn.commit()
        budget_id = cursor.lastrowid  # Fetch the inserted budget_id
        conn.close()

        # Redirect back to home screen
        await self.homescreen(widget)

    #Event handler: user selects a saved budget from the home screen to view/edit
    async def view_edit_budget(self, widget):

        #Retrieve the month and year of the budget
        month = widget.value.data[0]
        year = widget.value.data[1]
        
        #Display the budget
        self.display_budget(month, year)

    #Helper function to display a saved budget
    def display_budget(self, month, year):
        
        # Connect to MySQL Server
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        #Define a new screen in which to display the specified budget
        bg = self.empty_box()
        budget_display = toga.Box(
            style = Pack(
                background_color = "#C0E4B8",
                direction = COLUMN,
                padding = (0, 10)
            )
        )

        #Retrieve the budget data from the database
        cursor.execute(f"USE {MYSQL_DATABASE}")
        cursor.execute('''
        SELECT * FROM budgets WHERE client_id = %s AND year = %s AND month = %s
        ''', (self.client_id, year, month))
        self.budget_info = cursor.fetchall()
        conn.close()

        # Display the budget title
        month_names = ["January", "February", "March", "April", "May", "June", 
                       "July", "August", "September", "October", "November", "December"]
        budget_title = toga.Label(f"{month_names[month - 1]} {year}'s Budget", 
            style = Pack(
                font_size = 20, 
                font_weight = "bold",
                color = "#000000",
                background_color = "#C0E4B8"
            )
        )
        budget_display.add(budget_title)

        #Retrieve the first section name and make a section box
        prev_section = self.budget_info[0][2]
        section_box = self.section_display(prev_section)

        #Display the remaining budget information
        for subcat in self.budget_info:
            section = subcat[2] #Get section heading

            #If the current section is still the previous section:
            if(section == prev_section):
                
                #Add the subsection to the display
                subcat_box = self.subsection_display(subcat)
                section_box.add(subcat_box)
            
            #Otherwise, if we have hit a new section:
            else:

                #Add the previous section box to budget_display
                budget_display.add(section_box)

                #Retrieve the section name and make a new section box
                prev_section = section
                section_box = self.section_display(prev_section)

                #Add the subsection to the display
                subcat_box = self.subsection_display(subcat)
                section_box.add(subcat_box)

        #Add the latest section box to budget_display
        budget_display.add(section_box)

        #Add budget_display to the background box
        bg.add(budget_display)

        #Make the income/expense button
        in_ex = toga.Button(
            "Income/Expense +/-",
            on_press = partial(self.exp_income, month = month, year = year),
            style = Pack(
                background_color="#62C54C",
                padding=(10, 0, 0),
                width=250, 
                height=50, 
                font_weight="bold", 
                font_size=14, 
                color="#000000"
            )
        )

        #Make a home button
        home_button = toga.Button(
            "Home",
            on_press=self.homescreen,
            style=Pack(
                background_color="#62C54C",
                padding=(10, 0, 10),
                width=150, 
                height=50, 
                font_weight="bold", 
                font_size=14, 
                color="#000000"
            )
        )
        bg.add(in_ex, home_button)

        #Make the background a scroll container 
        scroll_container = toga.ScrollContainer(
            content = bg,
            horizontal = False,
            style = Pack(
                padding = 10
            )
        )
        
        #Make the scroll container the main content of the app
        self.main_window.content = scroll_container
        self.main_window.show()
    
    #Event handler to open the "Add Expense/Income" screen
    async def exp_income(self, widget, *, month, year, **kwargs):

        #Temporarily remove the "Income/Expense +/-" and "Home" buttons
        parent_box = widget.parent
        home_button = parent_box.children[parent_box.index(widget) + 1]
        parent_box.remove(home_button, widget)

        month_names = ["January", "February", "March", "April", "May", "June", 
                       "July", "August", "September", "October", "November", "December"]
        month_name = month_names[month - 1]

        #Create the background box for the input fields to go inside of
        bg = toga.Box(
            style = Pack(
                background_color = "#C0E4B8", 
                direction = COLUMN
            )
        )
        fields = toga.Box(
            style = Pack(
                background_color = "#C0E4B8", 
                direction = COLUMN, 
                width = 350, 
                padding= (15, 10)
            )
        )

        #Add a title
        budget_title = toga.Label(f"Add Transaction to {month_name} {year}'s Budget", 
            style = Pack(
                font_size = 15, 
                font_weight = "bold",
                color = "#000000",
                background_color = "#C0E4B8"
            )
        )
        fields.add(budget_title)
        
        #Define user input fields for making a transaction and add them

        #Income/Expense selection
        ie_box = toga.Box(
            style = Pack(
                background_color = "#C0E4B8",
                direction = ROW,
                alignment = CENTER,
                padding = (15, 0, 0)
            )
        )
        ie_label = toga.Label(
            "Income or Expense:",
            style=Pack(
                background_color="#C0E4B8",
                color="#000000",
                font_size=14
            )
        )
        self.ie_dropdown = toga.Selection(
            items = ["Income", "Expense"],
            style = Pack(width = 100)
        )
        ie_box.add(ie_label, self.ie_dropdown)
        fields.add(ie_box)
        
        #Section Selection
        section_box = toga.Box(
            style = Pack(
                background_color = "#C0E4B8",
                direction = ROW,
                alignment = CENTER,
                padding = (15, 0, 0)
            )
        )
        section_label = toga.Label(
            "Section:",
            style=Pack(
                background_color="#C0E4B8",
                color="#000000",
                font_size=14
            )
        )
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute(f"USE {MYSQL_DATABASE}")
        
        cursor.execute('''SELECT DISTINCT section FROM budgets 
            WHERE client_id = %s AND month = %s AND year = %s
            ''',
                       (self.client_id, month, year))
        result = cursor.fetchall()
        if result:
            section_selection = result
        else:
            print("Could not find section.")
            return
                       
        self.section_dropdown = toga.Selection(
            items = section_selection,
            style = Pack(width = 100),
            on_change = partial(self.update_subsections, month = month, year = year),
        )
        section_box.add(section_label, self.section_dropdown)
        fields.add(section_box)
        
        #Subsection Selection
        subsection_box = toga.Box(
            style = Pack(
                background_color = "#C0E4B8",
                direction = ROW,
                alignment = CENTER,
                padding = (15, 0, 0)
            )
        )
        subsection_label = toga.Label(
            "Subsection:",
            style=Pack(
                background_color="#C0E4B8",
                color="#000000",
                font_size=14
            )
        )
        
        cursor.execute('''SELECT subsection FROM budgets WHERE client_id = %s AND section = %s
        AND month = %s AND year = %s''',
                       (self.client_id, self.section_dropdown.value, month, year))
        result = cursor.fetchall()
        if result:
            subsection_selection = result
        else:
            print("Could not find subsection.")
            return
                       
        self.subsection_dropdown = toga.Selection(
            items = subsection_selection,
            style = Pack(width = 100)
        )
        subsection_box.add(subsection_label, self.subsection_dropdown)
        fields.add(subsection_box)
        conn.close()

        #Date input fields
        date_box = toga.Box(
            style = Pack(
                background_color = "#C0E4B8",
                direction = ROW,
                alignment = CENTER,
                padding = (15, 0, 0)
            )
        )
        month_label = toga.Label(
            "Month:",
             style=Pack(
                background_color="#C0E4B8",
                color="#000000",
                font_size=12
            )           
        )
        self.month_input = toga.NumberInput(
            min = 1,
            max = 12,
            value = datetime.datetime.now().month,
            step = 1,
            style=Pack(width=50)
        )
        day_label = toga.Label(
            "Day:",
             style=Pack(
                background_color="#C0E4B8",
                color="#000000",
                font_size=12
            )           
        )

        self.day_input = toga.NumberInput(
            min = 1,
            max = 31,
            value = datetime.datetime.now().day,
            step = 1,
            style=Pack(width=50)
        ) 
        year_label = toga.Label(
            "Year:",
             style=Pack(
                background_color="#C0E4B8",
                color="#000000",
                font_size=12
            )           
        )
        #User can go back to previous year if need be
        self.year_input = toga.NumberInput(
            min = datetime.datetime.now().year - 1,
            value = datetime.datetime.now().year,
            step = 1,
            style=Pack(width=75)
        ) 
        date_box.add(month_label, self.month_input,
                     day_label, self.day_input, 
                     year_label, self.year_input)
        fields.add(date_box)

        #Amount input field
        amount_box = toga.Box(
            style = Pack(
                background_color = "#C0E4B8",
                direction = ROW,
                alignment = CENTER,
                padding = (15, 0, 0)
            )
        )
        amount_label = toga.Label(
            "Amount:",
             style=Pack(
                background_color="#C0E4B8",
                color="#000000",
                font_size=14
            )           
        )
        self.amount_input = toga.NumberInput(
            min = 0,
            value = 0,
            step = 0.01,
            style=Pack(width=100)
        )
        amount_box.add(amount_label, self.amount_input)
        fields.add(amount_box)   

        #Merchant input field
        self.merchant_input = self.user_text_input(fields, "Merchant:", "Merchant here")

        #Save button
        save_button = toga.Button(
            "Save Transaction",
            on_press = partial(self.save_transaction, month = month, year = year),
            style = Pack(
                background_color = "#62C54C",
                padding = (10, 0, 0),
                width = 250, 
                height = 50, 
                font_weight = "bold", 
                font_size = 14,
                color = "#000000"
            )
        )

        #Cancel button
        cancel_button = toga.Button(
            "Cancel",
            on_press = partial(self.close_transaction, month = month, year = year),
            style = Pack(
                background_color = "#62C54C",
                padding = (10, 0, 0),
                width = 150, 
                height = 50, 
                font_weight = "bold", 
                font_size = 14,
                color = "#000000"
            )
        )
        fields.add(save_button, cancel_button)
        bg.add(fields)

        #Show the input fields in a new window
        ie_window = toga.Window(
            title = "Add Transaction",
            content = bg,
            closable = False
        )

        ie_window.show()

    async def close_transaction(self, widget, *, month, year, **kwargs):
        widget.parent.parent.window.close()
        self.display_budget(month, year)
        
    async def save_transaction(self, widget, *, month, year, **kwargs):

        #Do not save the transaction if the amount is $0.00
        amount = float(self.amount_input.value)

        if amount == 0:
            invalid = toga.InfoDialog("Transaction Failed", "Please enter a non-zero dollar amount")
            await self.main_window.dialog(invalid)
            return

        #Do not save the transaction if no merchant is provided
        if self.merchant_input.value.replace(" ", "") == "":
            invalid = toga.InfoDialog("Transaction Failed", "Please enter a merchant name")
            await self.main_window.dialog(invalid)
            return
        
        #Connect to database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute(f"USE {MYSQL_DATABASE}")
        
        cursor.execute('''
        SELECT * FROM budgets WHERE client_id = %s AND section = %s AND subsection = %s
        AND month = %s AND year = %s''',
                        (self.client_id, self.section_dropdown.value, self.subsection_dropdown.value,
                        month, year))
        result = cursor.fetchone()
        if result:
            budget_id = result[0]
        else:
            print("Could not find budget_id.")
            return
        
        try:
            date_object = datetime.date(
                int(self.year_input.value),
                int(self.month_input.value),
                int(self.day_input.value)
            )
        except ValueError:
            invalid = toga.InfoDialog("Transaction Failed", "Invalid date")
            await self.main_window.dialog(invalid)
            return
        
        cursor.execute('''
            INSERT INTO transactions (client_id, budget_id, date, amount, merchant, expense)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
                       (self.client_id, budget_id, date_object, amount, self.merchant_input.value,
                       True if self.ie_dropdown.value == "Expense" else False))
                       
        #Update Budget Totals
        if self.ie_dropdown.value == "Expense":
            # Subtract from total for expenses
            cursor.execute(
            "UPDATE budgets SET budget_total = budget_total - %s WHERE budget_id = %s",
            (amount, budget_id)
            )
        else:
            # Add to total for incomes
            cursor.execute(
                "UPDATE budgets SET budget_total = budget_total + %s WHERE budget_id = %s",
                (amount, budget_id)
            )
        conn.commit()
        conn.close()
        
        print("Transaction saved successfully.")

        #Close the transaction window and return to homescreen
        widget.parent.parent.window.close()
        self.display_budget(month, year)

    async def update_subsections(self, widget, *, month, year, **kwargs):
        selected_section = widget.value

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"USE {MYSQL_DATABASE}")
    
        cursor.execute('''
            SELECT subsection FROM budgets WHERE client_id = %s AND section = %s
            AND month = %s AND year = %s''',
            (self.client_id, selected_section, month, year)
        )
        results = cursor.fetchall()
        conn.close()

        if results:
            subsections = [row[0] for row in results]
            self.subsection_dropdown.items = subsections
        else:
            self.subsection_dropdown.items = []
            print("No subsections found.")

    #Helper function for making an empty background box with centered, "column" widget alignment
    def empty_box(self):
        return toga.Box(style=Pack(background_color="#C0E4B8", direction=COLUMN, alignment=CENTER))

    #Helper function for making section boxes and labels
    def section_display(self, title):

        #Set up a box for the section
        section_box = toga.Box(
            style = Pack(
                background_color = "#F5F5F5",
                direction = COLUMN,
                padding = 10
            )
        )

        #Make a label to add to the box
        section_label = toga.Label(
            title,
            style = Pack(
                font_size = 18,
                font_weight = "bold",
                color = "#000000",
                background_color = "#C0E4B8"
            )
        )
        section_box.add(section_label)
        return section_box
  
    #Helper function for making subsection boxes and labels
    def subsection_display(self, subcat):

        #Make a box for the subsection
        subcat_box = toga.Box(
            style = Pack(
                background_color = "#F5F5F5",
                direction = ROW,
                alignment = CENTER,
                padding = 5
            )
        )

        #Make labels for the subsection title and dollar amount
        subcat_label = toga.Label(
            subcat[3],
            style = Pack(
                width = 150,
                color = "#000000",
                background_color = "#F5F5F5"
            )
        )
        amount_label = toga.Label(
            f"${subcat[4]:.2f}",
            style = Pack(
                width = 100,
                text_align = RIGHT,
                color = "#000000",
                background_color = "#F5F5F5"
            )
        )
        subcat_box.add(subcat_label, amount_label)
        return subcat_box
    
    #Helper function to define startup screen
    def startscreen(self):
        main_box = self.empty_box() #Create a box for the background
        logo_img = toga.Image("DegreeDollarsLogo.png") #Imports the logo

        #An ImageView object is required to display the image
        view = toga.ImageView(logo_img, style=Pack(padding=(200, 0, 0), width=350, height=150))
        main_box.add(view)

        #Define the "Sign Up" and "Log In" buttons (store them in a box)
        sign_log = self.empty_box()

        #Sign Up button
        signup = toga.Button(
            "Sign Up",
            on_press=self.signup,
            style=Pack(background_color=("#F5F5F5"), padding=(35, 0, 20), width=300, height=55,
                       font_weight="bold", font_size=18)
        )
        sign_log.add(signup)

        #Log In button
        login = toga.Button(
            "Log In",
            on_press=self.login,
            style=Pack(background_color=("#F5F5F5"), padding=(0, 0, 200), width=300, height=55,
                       font_weight="bold", font_size=18)
        )
        sign_log.add(login)

        main_box.add(sign_log) #Add the box containing the buttons to the background box

        #Display the main_box in the main window
        self.main_window.content = main_box
        self.main_window.show()

    #Helper function to return to the startup screen, specifically when a button is pressed
    async def startscreen_button(self, widget):
        self.startscreen()

    #Create the signup screen
    async def signup(self, widget):
        parent_box=widget.parent #The parent box is the box containing the "Sign Up" and "Log In" buttons
        grandparent_box=parent_box.parent #The grandparent box is the background of the startup screen

        #Remove the parent box from the grandparent box
        grandparent_box.remove(parent_box)

        #Create a new box to add to the grandparent box that will contain the signup fields
        fields=toga.Box(style=Pack(background_color="#C0E4B8", direction=COLUMN, width=350))
        
        #Define user input fields for signing up and add them to the fields box
        self.first_name_input = self.user_text_input(fields, "First Name:", "First name here")
        self.last_name_input = self.user_text_input(fields, "Last Name:", "Last name here")
        self.username_input = self.user_text_input(fields, "Username:", "Username here")
        self.password_input = self.user_text_input(fields, "Password:", "Password here")
        self.password_confirmation_input = self.user_text_input(fields, "Confirm Password:", "Password here")

        #"Sign Up" and "Cancel" buttons
        buttons=toga.Box(style=Pack(background_color="#C0E4B8", color="#000000", direction=ROW, alignment=CENTER, padding=(15, 0, 0)))
        
        sign_up=toga.Button(
            "Sign Up",
            on_press=self.save_signup_data,
            style=Pack(background_color=("#F5F5F5"), width=160, height=50,
                        font_weight="bold", font_size=16, padding_right=30)
        )
        cancel=toga.Button(
            "Cancel",
            on_press=self.startscreen_button,
            style=Pack(background_color=("#F5F5F5"), width=160, height=50,
                        font_weight="bold", font_size=16)
        )
        buttons.add(sign_up, cancel)

        #Add the buttons to the "fields" box
        fields.add(buttons)

        #Add the "fields" box to the grandparent box
        grandparent_box.add(fields)

    #Create the login screen
    async def login(self, widget):
        parent_box=widget.parent #The parent box is the box containing the "Sign Up" and "Log In" buttons
        grandparent_box=parent_box.parent #The grandparent box is the background of the startup screen

        #Remove the parent box from the grandparent box
        grandparent_box.remove(parent_box)

        #Create a new box to add to the grandparent box that will contain the login fields
        fields=toga.Box(style=Pack(background_color="#C0E4B8", direction=COLUMN, width=350))
        
        #Define user input fields for logging in and add them to the fields box
        self.login_input = self.user_text_input(fields, "Username:", "Username here")
        self.password_input = self.user_text_input(fields, "Password:", "Password here")

        #"Log In" and "Cancel" buttons
        buttons=toga.Box(style=Pack(background_color="#C0E4B8", direction=ROW, alignment=CENTER,
                                    padding=(15, 0, 0)))
        log_in=toga.Button(
            "Log In",
            on_press=self.check_login_credentials,
            style=Pack(background_color=("#F5F5F5"), width=160, height=50,
                       font_weight="bold", font_size=16, padding_right=30)
        )
        cancel=toga.Button(
            "Cancel",
            on_press=self.startscreen_button,
            style=Pack(background_color=("#F5F5F5"), width=160, height=50,
                       font_weight="bold", font_size=16)
        )
        buttons.add(log_in, cancel)

        #Add the buttons to the "fields" box
        fields.add(buttons)

        #Add the "fields" box to the grandparent box
        grandparent_box.add(fields)       

    #Helper function to make a signup/login field
    def user_text_input(self, parent_box, field_label, placeholder_text):
        field_box=toga.Box(style=Pack(background_color="#C0E4B8", direction=ROW, alignment=CENTER,
                           padding=(15, 0, 0)))
        field_label=toga.Label(field_label, style=Pack(background_color="#C0E4B8", color="#000000", font_size=14))
        
        #TODO: Why is the password field not displaying text as dots?
        if field_label == "Password:" or field_label == "Confirm Password:":
            field_input=toga.PasswordInput(placeholder=placeholder_text, style=Pack(width=150, background_color="#F5F5F5", color="#000000"))
        else:
            field_input=toga.TextInput(placeholder=placeholder_text, style=Pack(width=150, background_color="#F5F5F5", color="#000000"))
            
        field_box.add(field_label, field_input)
        parent_box.add(field_box)
        return field_input
        
    #Save sign-up data to the database
    async def save_signup_data(self, widget):
        self.first_name = self.first_name_input.value
        self.last_name = self.last_name_input.value
        self.username = self.username_input.value
        self.password = self.password_input.value
        self.password_confirmation = self.password_confirmation_input.value

        signup_info = [self.first_name, self.last_name, self.username, self.password,
                       self.password_confirmation]

        #Display a dialog box if the user does not provide text in all input fields
        for value in signup_info:
            if value.replace(" ", "") == "":
                invalid = toga.InfoDialog("Sign Up Failed", "Please complete all fields")
                await self.main_window.dialog(invalid)
                return
        
        #Display a dialog box if the two password fields to not match
        if self.password != self.password_confirmation:
            invalid = toga.InfoDialog("Sign Up Failed", "Passwords do not match")
            await self.main_window.dialog(invalid)
            return
                
        #Connect to database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute(f"USE {MYSQL_DATABASE}")

        #Display a dialog box if the username or password already exist
        cursor.execute('''
            SELECT username, password FROM profile WHERE username = %s or password = %s
            ''',
                        (self.username, self.password))
        result = cursor.fetchall()
        if result:
            invalid = toga.InfoDialog("Sign Up Failed", "Username or password already exist")
            await self.main_window.dialog(invalid)
            return

        #If none of the above errors are caught, save the account info
        cursor.execute('''
            INSERT INTO profile (first_name, last_name, username, password)
            VALUES (%s, %s, %s, %s)
            ''',
                       (self.first_name, self.last_name, self.username, self.password))
                       
        conn.commit()
        conn.close()
        
        print("Account created successfully.")
        await self.homescreen(widget)
        
    async def check_login_credentials(self, widget):
        username = self.login_input.value
        password = self.password_input.value
        
        #Connect to database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"USE {MYSQL_DATABASE}")
        cursor.execute('''
            SELECT * FROM profile WHERE username = %s AND password = %s
            ''',
                       (username, password))
                       
        result = cursor.fetchone()
        
        if result:
            print("Login successful.")
            self.client_id = result[0]
            self.username = username
            self.password = password
            await self.homescreen(widget)
        
        else:
            invalid = toga.InfoDialog("Login Failed", "Invalid username or password")
            await self.main_window.dialog(invalid)
            
        conn.close()
    
    #Create See My History feature
    async def see_my_history(self, widget):
        month, year = widget.value.data
        
        await self.display_transaction_history(month, year)
        
    async def display_transaction_history(self, month, year):
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"USE {MYSQL_DATABASE}")
    
        # Get transaction info for this month/year for this user
        cursor.execute('''
            SELECT t.date, b.section, b.subsection, t.amount, t.merchant, t.expense
            FROM transactions t
            JOIN budgets b ON t.budget_id = b.budget_id
            WHERE t.client_id = %s AND MONTH(t.date) = %s AND YEAR(t.date) = %s
            ORDER BY t.date DESC
        ''', (self.client_id, month, year))

        transactions = cursor.fetchall()
        conn.close()
        
        #Build UI
        history_box = self.empty_box()
        month_name = datetime.date(1900, month, 1).strftime('%B') # converts the number to the month
        title = toga.Label(
            f"Transaction History — {month_name} {year}",
            style=Pack(font_size=24, font_weight="bold", background_color="#C0E4B8", color="#000000", padding=(10, 0))
                           )
        history_box.add(title)
        
        if transactions:
            for trans in transactions:
                date, section, subsec, amount, merchant, is_expense = trans
                color = "#d9534f" if is_expense else "#5cb85c"
                sign = "-" if is_expense else "+"
                
                #Style of each transaction
                card = toga.Box(
                    style=Pack(
                        direction=ROW,
                        padding=10,
                        background_color="#F5F5F5",
                        width=350,
                        alignment=CENTER
                    )
                )
                
                #Amount Box
                amount_label = toga.Label(
                    f"{sign}${amount:.2f}",
                    style=Pack(font_size=18, background_color="#F5F5F5", color=color, padding_bottom=5)
                )
                
                amount_box = toga.Box(
                    style=Pack(direction=COLUMN, alignment=LEFT, background_color="#F5F5F5", width=80)
                )
                
                amount_box.add(amount_label)
                
                #Text Box
                merchant_label = toga.Label(
                    merchant,
                    style=Pack(font_size=16, background_color="#F5F5F5", color="#000000", padding_bottom=3)
                )
                subsection_label = toga.Label(
                    subsec.capitalize(),
                    style=Pack(font_size=18, background_color="#F5F5F5", font_weight="bold", color="#000000", padding_bottom=5)
                )
                
                text_box = toga.Box(
                    style=Pack(direction=COLUMN, background_color="#F5F5F5", width=160)
                )
                text_box.add(subsection_label, merchant_label)
                
                #Date Box
                month_label = toga.Label(
                    date.strftime('%b'),
                    style=Pack(font_size=14, font_weight="bold", background_color="#F5F5F5", color="#000000", text_align=CENTER)
                )
                day_label = toga.Label(
                    str(date.day),
                    style=Pack(font_size=14, background_color="#F5F5F5", color="#000000", text_align=CENTER)
                )
                
                date_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, width=50, padding_right=10))
                date_box.add(month_label, day_label)

                card.add(date_box, text_box, amount_box)
                history_box.add(card)
                
        else:
            history_box.add(toga.Label("No transactions found.", style=Pack(font_size=14, background_color="#C0E4B8", color="#000000", padding=10)))
            
        history_box.add(title)

        back_btn = toga.Button("Back to Home", on_press=self.homescreen, style=Pack(padding=10, width=150))
        history_box.add(back_btn)
            
        scroll = toga.ScrollContainer(content=history_box, horizontal=False, style=Pack(padding=10))
        self.main_window.content = scroll
        self.main_window.show()
        
    async def change_username(self, widget):
        parent_box = widget.parent
        grandparent_box = parent_box.parent
        grandparent_box.clear()
        
        #Establish SQL connection
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"USE {MYSQL_DATABASE}")
        
        #Title
        
        #Greeting
        greeting_container = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, background_color="white", padding=20, width=500))

        greeting_label = toga.Label(
        f"Change Username",
        style=Pack(font_size=18, font_weight="bold", padding=(20, 0), background_color="white")
        )
        greeting_container.add(greeting_label)
        
        #Change username
        change_username_container = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, background_color="white", padding=20, width=500))
        
        new_username = self.user_text_input(change_username_container, "New Username:", "New username here")
        
        async def submit_username_change(button):
            #Establish SQL connection
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute(f"USE {MYSQL_DATABASE}")
            
            # Update password in profile table
            cursor.execute('''
                SELECT username
                FROM profile
            ''')
        
            result = cursor.fetchall()
            
            if (new_username.value,) in result:
                not_possible = toga.Label("That username is already in use.", style=Pack(color="red", padding_top=10))
                change_username_container.add(not_possible)
                await asyncio.sleep(1.5)
                change_username_container.remove(not_possible)
            else:
                # Update username in profile table
                cursor.execute('''
                    UPDATE profile
                    SET username = %s
                    WHERE client_id = %s
                ''', (new_username.value, self.client_id))
                conn.commit()
                
                self.username = new_username.value
                
                success_msg = toga.Label("Username changed successfully!", style=Pack(color="#5cb85c", padding_top=10))
                change_username_container.add(success_msg)

                await asyncio.sleep(1.5)
                await self.homescreen(widget)
        
        submit_btn = toga.Button("Submit", on_press=submit_username_change, style=Pack(padding=10))
        change_username_container.add(submit_btn)

        grandparent_box.add(greeting_container, change_username_container)

        cursor.close()
    
        conn.close()

    async def change_password(self, widget):
        parent_box = widget.parent
        grandparent_box = parent_box.parent
        grandparent_box.clear()
        
        #Establish SQL connection
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"USE {MYSQL_DATABASE}")
        
        #Title
        
        #Greeting
        greeting_container = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, background_color="white", padding=20, width=500))

        greeting_label = toga.Label(
        f"Change Password",
        style=Pack(font_size=18, font_weight="bold", padding=(20, 0), background_color="white")
        )
        greeting_container.add(greeting_label)
        
        #Change username
        change_password_container = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, background_color="white", padding=20, width=500))
        
        new_password = self.user_text_input(change_password_container, "New Password:", "New password here")
        
        async def submit_password_change(button):
            #Establish SQL connection
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute(f"USE {MYSQL_DATABASE}")
            
            # Update password in profile table
            cursor.execute('''
                SELECT password
                FROM profile
            ''')
        
            result = cursor.fetchall()
            
            if (new_password.value,) in result:
                not_possible = toga.Label("That password is already in use.", style=Pack(color="red", padding_top=10))
                change_password_container.add(not_possible)
                await asyncio.sleep(1.5)
                change_password_container.remove(not_possible)

            else:
                # Update password in profile table
                cursor.execute('''
                    UPDATE profile
                    SET password = %s
                    WHERE client_id = %s
                ''', (new_password.value, self.client_id))
                conn.commit()
                
                self.password = new_password.value
                
                success_msg = toga.Label("Password changed successfully!", style=Pack(color="#5cb85c", padding_top=10))
                change_password_container.add(success_msg)

                await asyncio.sleep(1.5)
                await self.homescreen(widget)
        
        submit_btn = toga.Button("Submit", on_press=submit_password_change, style=Pack(padding=10))
        change_password_container.add(submit_btn)

        grandparent_box.add(greeting_container, change_password_container)

        cursor.close()
    
        conn.close()
        
def main():
    return DegreeDollars()
