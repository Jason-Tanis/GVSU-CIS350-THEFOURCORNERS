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
        addexp  = self.empty_box()
        home    = self.empty_box()

        # Add username to Profile tab
        username_label = toga.Label(
        f"Hello, {self.username}! Welcome to your Profile!",
        style=Pack(font_size=18, font_weight="bold", padding=(20, 0), background_color="#C0E4B8")
        )
        profile.add(username_label)

        # Homescreen
        # Create New Budget Button
        create_budget_box = self.empty_box()
        create_budget_button = toga.Button(
            "Create New Budget",
            on_press=self.create_budget_view,
            style=Pack(background_color="#62C54C", padding=(35, 0, 35),
            width=300, height=55, font_weight="bold", font_size=18,color="#000000")
        )
        create_budget_box.add(create_budget_button)
        home.add(create_budget_box)

        #Create navigation bar as an OptionContainer
        navbar = toga.OptionContainer(
                style = Pack(background_color = ("#62C54C")),
                content = [
                    toga.OptionItem("Profile", profile, icon = toga.Icon("PTab")),
                    toga.OptionItem("Home", home, icon = toga.Icon("HTab")),
                    toga.OptionItem("Loan Planner", loan, icon = toga.Icon("LTab")),
                    toga.OptionItem("History", addexp, icon = toga.Icon("ATab"))
                ]
        )

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

        #List for displaying dropdown menu options (initially contains only a placeholder dictionary)
        dropdown_options = [{"name": "Select Budget", "data": (-1, -1)}]

        #List of month names
        month_names = ["January", "February", "March", "April", "May", "June", 
                       "July", "August", "September", "October", "November", "December"]
        
        #If the user has saved at least one budget,
        #create and add a dropdown menu to select one of the saved budgets
        if all_budgets:
            for budget in all_budgets:
                month_name = month_names[budget[0] - 1]
                year = budget[1]
                budget_title = f"{month_name} {year}"
                tmp_dictionary = {"name": budget_title, "data": budget}
                dropdown_options.append(tmp_dictionary)
            print(dropdown_options)
            selectbudget_label = toga.Label(
                "View/Edit Budget",
                style = Pack(
                    font_size = 14,
                    font_weight = "bold",
                    color = "#000000",
                    background_color = "#C0E4B8",
                    text_align = CENTER
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
                    text_align = CENTER
                )
            )
            home.add(selectbudget_label)
        
        # conn.close()
        # Loan Planner

        loan_planner_label = toga.Label("Loan Payment Planner", style=Pack(font_size=18, font_weight="bold", padding=10,color="#000000"))
        prompt_text_1 = toga.Label("Please enter the following information:", style=Pack(font_size=12, font_weight="bold", text_align=CENTER,color="#000000"))
        dollar_amount_box = toga.Box(style=Pack(padding=(5, 5), direction=ROW, alignment=LEFT))
        dollar_amount_label = toga.Label("Total dollar amount of loan:", style=Pack(font_size=18, text_align=LEFT,color="#000000"))
        dollar_amount_input = toga.NumberInput(min=0.00, value=0.00, step=5, style=Pack(width=100, padding=(5, 5)))
        dollar_amount_box.add(dollar_amount_label, dollar_amount_input)
        interest_rate_box = toga.Box(style=Pack(padding=(5, 5), direction=ROW, alignment=LEFT))
        interest_rate_label = toga.Label("Interest rate of loan (APR):", style=Pack(font_size=18, text_align=LEFT,color="#000000"))
        interest_rate_input = toga.NumberInput(min=0.00, value=0.00, step=5, style=Pack(width=100, padding=(5, 5)))
        interest_rate_box.add(interest_rate_label, interest_rate_input)
        buttons_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
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
        buttons_box.add(calculate_payment_button, calculate_timeline_button)
        loan.add(loan_planner_label, prompt_text_1, dollar_amount_box, interest_rate_box, buttons_box)

        #Display the homescreen contents
        self.main_window.content = navbar
        self.main_window.show()


    async def calculate_payment(self, widget): # Calculate the payment required for the timeline

        parent_box = widget.parent # buttons box
        grandparent_box = parent_box.parent # loan
        loan_amount = grandparent_box.children[2].children[1].value
        interest_rate = grandparent_box.children[3].children[1].value
        grandparent_box.clear()
        payment_calculator_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        timeline_box = toga.Box(style=Pack(padding=(5, 5), direction=ROW, alignment=LEFT))
        timeline_label = toga.Label("Months to pay off:", style=Pack(font_size=18, text_align=LEFT,color="#000000"))
        timeline_input = toga.NumberInput(min=0.00, value=0.00, step=1, style=Pack(width=100, padding=(5, 5)))
        timeline_box.add(timeline_label, timeline_input)
        calculate_payment_button_final = toga.Button(
            "Compute!",
            on_press=partial(self.calculate_payment_math, loan_amount, interest_rate),
            style=Pack(font_size=18, width=400, height=40, padding=10, color="#000000")
        )
        payment_calculator_box.add(timeline_box, calculate_payment_button_final)
        print(payment_calculator_box)
        grandparent_box.add(payment_calculator_box)
    
    async def calculate_payment_math(self, loan_amount, interest_rate, widget):
        parent_box = widget.parent # payment_calculator_box
        grandparent_box = parent_box.parent # loan
        results_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        months = parent_box.children[0].children[1].value
        Results_label = toga.Label("Results", style=Pack(font_size=24, text_align=LEFT, font_weight="bold"))
        dollar_amount_label_final = toga.Label(f"Total loan amount: ${loan_amount}", style=Pack(font_size=18, text_align=LEFT))
        interest_rate_label_final = toga.Label(f"Interest rate: {interest_rate}%", style=Pack(font_size=18, text_align=LEFT))
        months_label_final = toga.Label(f"Planned duration: {months} months", style=Pack(font_size=18, text_align=LEFT))

        monthly_interest_rate = interest_rate / 12 / 100
        recommendation = (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate)**months) / ((1 + monthly_interest_rate)**months - 1)
        recommendation_label = toga.Label("Recommended monthly payment:", style=Pack(font_size=24, text_align=CENTER))
        recommendation_output = toga.Label(f"${recommendation:.2f} per month", style=Pack(font_size=36, text_align=CENTER))

        results_box.add(Results_label, dollar_amount_label_final, interest_rate_label_final, months_label_final, recommendation_label, recommendation_output)
        grandparent_box.add(results_box)

        
    async def calculate_timeline(self, widget): # Calculate the timeline from data
        parent_box = widget.parent # buttons box
        grandparent_box = parent_box.parent # loan
        loan_amount = grandparent_box.children[2].children[1].value
        interest_rate = grandparent_box.children[3].children[1].value
        grandparent_box.clear()
        timeline_calculator_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        payment_box = toga.Box(style=Pack(padding=(5, 5), direction=ROW, alignment=LEFT))
        payment_label = toga.Label("Amount of monthly payment:", style=Pack(font_size=18, text_align=LEFT))
        payment_input = toga.NumberInput(min=0.00, value=0.00, step=10, style=Pack(width=100, padding=(5, 5)))
        payment_box.add(payment_label, payment_input)
        calculate_timeline_button_final = toga.Button(
            "Compute!",
            on_press=partial(self.calculate_timeline_math, loan_amount, interest_rate),
            style=Pack(font_size=18, width=400, height=40, padding=10)
        )
        timeline_calculator_box.add(payment_box, calculate_timeline_button_final)
        grandparent_box.add(timeline_calculator_box)

    async def calculate_timeline_math(self, loan_amount, interest_rate, widget):
        parent_box = widget.parent # payment_calculator_box
        grandparent_box = parent_box.parent # loan
        results_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        payment = parent_box.children[0].children[1].value
        Results_label = toga.Label("Results", style=Pack(font_size=24, text_align=LEFT, font_weight="bold"))
        dollar_amount_label_final = toga.Label(f"Total loan amount:     ${loan_amount}", style=Pack(font_size=18, text_align=CENTER))
        interest_rate_label_final = toga.Label(f"Interest rate:     {interest_rate}%", style=Pack(font_size=18, text_align=CENTER))
        months_label_final = toga.Label(f"Planned monthly payment:     ${payment}", style=Pack(font_size=18, text_align=CENTER))

        monthly_interest_rate = interest_rate / 12 / 100
        recommendation = (math.log(payment / (payment - loan_amount * monthly_interest_rate))) / (math.log(1 + monthly_interest_rate))
        recommendation_label = toga.Label("Recommended payment duration:", style=Pack(font_size=24, text_align=CENTER))
        recommendation_output = toga.Label(f"{recommendation:.0f} months", style=Pack(font_size=36, text_align=CENTER))

        results_box.add(Results_label, dollar_amount_label_final, interest_rate_label_final, months_label_final, recommendation_label, recommendation_output)
        grandparent_box.add(results_box)


    async def create_budget_view(self, widget): #New viewing screen for creating new budget
        budget_box = self.empty_box()

        #Title
        title = toga.Label("Create New Budget", style=Pack(background_color="#C0E4B8", color="#000000", font_size=24, font_weight="bold", padding=(10, 0)))
        budget_box.add(title)

        #Add a box in which the user can specify the current month
        spacer = toga.Box(style=Pack(background_color="#C0E4B8", direction=COLUMN, padding=(0,10)))
        month_box = toga.Box(style=Pack(background_color="#C0E4B8", direction=ROW, alignment=CENTER))
        year_box = toga.Box(style=Pack(background_color="#C0E4B8", direction=ROW, alignment=CENTER))

        monthfield_label = toga.Label("Month", style=Pack(color="#000000", font_size=18, padding_left=10))
        yearfield_label = toga.Label("Year", style=Pack(color="#000000", font_size=18, padding_left=10))
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
            style=Pack(background_color="#62C54C", padding=(10, 0, 10), width=200, height=50, font_weight="bold", font_size=18,color="#000000")
        )
        budget_box.add(save_button)

        #For Scrolling
        scroll_container = toga.ScrollContainer(content=budget_box, horizontal=False, style=Pack(padding=10))
        
        self.main_window.content = scroll_container
        self.main_window.show()
        
    def create_budget_section(self, section):
        section_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # title
        section_label = toga.Label(section, style=Pack(font_size=20, font_weight="bold",color="#000000"))
        print(section_label)
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

        #Current Budget
        cursor.execute('''
        SELECT budget_id FROM budgets WHERE client_id = %s AND year = %s AND month = %s
        ''', (self.client_id, year, selected_month_number))

        budget_we_on = cursor.fetchone()

        # Iterate through sections and save them
        for section in self.main_window.content.content.children[2:-1]:
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
        year = widget.value.data[1]
        month = widget.value.data[0]

        #Stop the function if the user pressed the "Select Budget" placeholder
        if(year == -1 and month == -1):
            return
        
        # Create database if one isn't already created
        create_database(self)
        
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
        print(self.budget_info)
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

        #Add a home button
        home_button = toga.Button(
            "Home",
            on_press=self.homescreen,
            style=Pack(
                background_color="#62C54C",
                padding=(10, 0, 0),
                width=150, 
                height=50, 
                font_weight="bold", 
                font_size=14, 
                color="#000000"
            )
        )
        bg.add(home_button)

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
    async def exp_income(self, widget, *, budget_row, **kwargs):

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
        #Note: budget_row[0] = budget_id of subcategory
        #      budget_row[1] = client_id
        #      budget_row[2] = category
        #      budget_row[3] = subcategory
        #      budget_row[4] = amount
        #      budget_row[5] = month
        #      budget_row[6] = year
        #All seven values are needed to save a transaction and 
        #update the appropriate row in the "budgets" table accordingly
        budget_title = toga.Label(f"Add Transaction to {budget_row[3]} ({budget_row[2]})", 
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
        
        cursor.execute(f'''SELECT * FROM budgets WHERE client_id = %s
            ''',
                       (self.client_id,))
        result = cursor.fetchall()
        if result:
            section_selection = [row[2] for row in result]
        else:
            print("Could not find section.")
            return
                       
        self.section_dropdown = toga.Selection(
            items = section_selection,
            style = Pack(width = 100)
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
        
        cursor.execute(f'''SELECT * FROM budgets WHERE client_id = %s AND section = %s
            ''',
                       (self.client_id,self.section_dropdown.value))
        result = cursor.fetchall()
        if result:
            subsection_selection = [row[3] for row in result]
        else:
            print("Could not find subsection.")
            return
                       
        self.subsection_dropdown = toga.Selection(
            items = subsection_selection,
            style = Pack(width = 100)
        )
        subsection_box.add(subsection_label, self.subsection_dropdown)
        fields.add(subsection_box)


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
        #TODO: currently, the user can input invalid dates because the max
        #does not account for months with only 30 days, or February/leap years...
        #how do we prevent these invalid values from being saved? Can we use datetime in Python?
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
            on_press = self.save_transaction,
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
        fields.add(save_button)
        bg.add(fields)

        #Show the input fields in a new window
        ie_window = toga.Window(
            title = "Add Income/Expense",
            content = bg
        )

        ie_window.show()
        
    async def save_transaction(self, widget):
        
        #Connect to database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute(f"USE {MYSQL_DATABASE}")
        
        cursor.execute(f"SELECT * FROM budgets WHERE client_id = %s AND section = %s AND subsection = %s",
                        (self.client_id, self.section_dropdown.value, self.subsection_dropdown.value))
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
            print("Invalid date.")
            return
        
        amount = float(self.amount_input.value)
        
        cursor.execute('''
            INSERT INTO transactions (client_id, budget_id, date, amount, merchant, expense)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
                       (self.client_id, budget_id, date_object, amount, self.merchant_input.value, True if self.ie_dropdown.value == "Expense" else False))
                       
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
        await self.homescreen(widget)

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
                width = 100,
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

        #Make the income/expense button
        in_ex = toga.Button(
            "+/-",
            on_press = partial(self.exp_income, budget_row = subcat),
            style = Pack(
                background_color="#62C54C",
                width=40, height=25, font_weight="bold", color="#000000"
            )
        )
        subcat_box.add(subcat_label, amount_label, in_ex)
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
        
        #Password validation
        if self.password != self.password_confirmation:
            print("Passwords do not match.")
            return
                
        #Connect to database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute(f"USE {MYSQL_DATABASE}")
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
            print("Invalid username or password")
            
        conn.close()
        
        
def main():
    return DegreeDollars()
