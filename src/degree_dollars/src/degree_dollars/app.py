"""
A budgeting application for undergraduate and graduate college students
"""

import toga
import os
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, RIGHT
import mysql.connector
import datetime

# MySQL Connection Settings
MYSQL_HOST = "localhost"  # Change if using a remote server and edit below contents
MYSQL_USER = "create_username"
MYSQL_PASSWORD = "create_password"
MYSQL_DATABASE = "degree_dollars"

# Get the correct app storage directory
def get_database_path(app):
    """Returns the correct database path inside the app's data directory."""
    db_path = app.paths.data / "degree_dollars.db"  # Get writable path
    os.makedirs(app.paths.data, exist_ok=True)  # Ensure directory exists
    return str(db_path)

def create_database(app):
    """Creates the MySQL database and necessary tables if they don’t exist."""
    db_path = get_database_path(app)  # Get correct database path
    print(f"Database path: {db_path}")  # Debugging: Check if path is correct

    try:
        # Connect to MySQL Server
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = conn.cursor()
        
        # Create Database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        cursor.execute(f"USE {MYSQL_DATABASE}")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile (
        client_id INTEGER PRIMARY KEY,
        password VARCHAR(255) NOT NULL, --hash the password before storing in db
        email VARCHAR(50) NOT NULL,
        first_name VARCHAR(50),
        last_name VARCHAR(50)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget (
        client_id INTEGER,
        section CHAR(50),
        subsection CHAR(50) PRIMARY KEY,
        budget_total NUMERIC,
        month INTEGER, --1 through 12 will be stored
        year INTEGER,
        
        FOREIGN KEY (client_id)
            REFERENCES profile(client_id)
            ON DELETE CASCADE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY,
        client_id INTEGER,
        section CHAR(50),
        subsection CHAR(50),
        date DATE,
        amount NUMERIC,
        merchant CHAR(50),
        expense BOOL,

        FOREIGN KEY (client_id)
            REFERENCES profile(client_id)
            ON DELETE CASCADE,
    
        FOREIGN KEY (subsection)
            REFERENCES budget(subsection)
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
        
        #This is the box that opens upon startup; all elements inside the box are to be vertically stacked (COLUMN),
        #and center-aligned (CENTER)
        main_box = toga.Box(style=Pack(background_color=("#C0E4B8"), direction=COLUMN, alignment=CENTER))
        logo_img = toga.Image("DegreeDollarsLogo.png") #Imports the logo

        #An ImageView object is required to view the image
        view = toga.ImageView(logo_img, style=Pack(padding=(200, 0, 0), width=350, height=150))
        main_box.add(view)

        #Define the "View my Budgets" button
        button = toga.Button(
            "View My Budgets",
            on_press=self.homescreen,
            style=Pack(background_color=("#F5F5F5"), padding=(35, 0, 200), width=300, height=55,
                       font_weight="bold", font_size=18)
        )
        main_box.add(button)

        self.main_window = toga.MainWindow(title=self.formal_name) #Window in which box is displayed
        self.main_window.content = main_box
        self.main_window.show()

    async def homescreen(self, widget): #Open the Home Screen of the app

        #Create boxes for each navigation bar tab (currently, they are all empty boxes except for home content)
        profile = self.empty_box()
        loan    = self.empty_box()
        addexp  = self.empty_box()
        home    = self.empty_box()

        # Homescreen
        # Create New Budget Button
        create_budget_box = self.empty_box()
        create_budget_button = toga.Button(
            "Create New Budget",
            on_press=self.create_budget_view,
            style=Pack(background_color="#62C54C", padding=(35, 0, 35),
            width=300, height=55, font_weight="bold", font_size=18)
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
                    toga.OptionItem("Add Expense", addexp, icon = toga.Icon("ATab"))
                ]
        )

        #Make "Home" the currently open tab
        navbar.current_tab = "Home"
        
        # Connect to database
        db_path = get_database_path(self)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all budgets for the latest month
        cursor.execute("SELECT DISTINCT month FROM budgets WHERE user_id = 1 ORDER BY id DESC LIMIT 1")
        latest_month = cursor.fetchone()
        if latest_month:
            latest_month = latest_month[0]
            cursor.execute("SELECT category, subcategory, amount FROM budgets WHERE user_id = 1 AND month = ?", (latest_month,))
            budget_data = cursor.fetchall()
        else:
            budget_data = []

        conn.close()

        # Display the budget
        if budget_data:
            month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            budget_title = toga.Label(f"{month_names[latest_month-1]}'s Budget", style=Pack(font_size=20, font_weight="bold"))
            home.add(budget_title)

            current_category = None
            category_box = None

            for category, subcategory, amount in budget_data:
                if category != current_category:
                    current_category = category
                    category_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
                    category_label = toga.Label(category, style=Pack(font_size=18, font_weight="bold"))
                    category_box.add(category_label)
                    home.add(category_box)

                sub_box = toga.Box(style=Pack(direction=ROW, padding=5))
                sub_label = toga.Label(subcategory, style=Pack(width=150))
                amount_label = toga.Label(f"${amount:.2f}", style=Pack(width=100, text_align=RIGHT))

                sub_box.add(sub_label, amount_label)
                category_box.add(sub_box)
    
        else:
            home.add(toga.Label("No budget found. Create a new one!"))


        #Display the homescreen contents
        self.main_window.content = navbar
        self.main_window.show()

    async def create_budget_view(self, widget): #New viewing screen for creating new budget
        budget_box = self.empty_box()

        #Title
        title = toga.Label("Create New Budget", style=Pack(background_color="#C0E4B8", color="#000000", font_size=24, font_weight="bold", padding=(10, 0)))
        budget_box.add(title)

        #Add a box in which the user can specify the current month
        spacer = toga.Box(style=Pack(background_color="#C0E4B8", direction=COLUMN, padding=(0,10)))
        month_box = toga.Box(style=Pack(background_color="#C0E4B8", direction=ROW, alignment=CENTER))
        monthfield_label = toga.Label("'s Budget", style=Pack(color="#000000", font_size=18,padding_left=10))
        months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
        current_month_index = datetime.datetime.now().month - 1
        self.month_selection = toga.Selection(items=months, value=months[current_month_index], style=Pack(width=250))
    
        month_box.add(monthfield_label, self.month_selection)
        spacer.add(month_box)
        budget_box.add(spacer)

        #Predefined categories (just to fill in space)
        categories = ["Education", "Housing/Utilities", "Food", "Transportation", "Entertainment"]
        for category in categories:
            section_box = self.create_budget_section(category)
            budget_box.add(section_box)

        #Box to contain "Add Section" and "Save Budget" buttons
        add_save_box = self.empty_box()

        # "Add Section" Button
        add_section_button = toga.Button(
            "Add Section +", on_press=self.add_budget_section,
            style=Pack(font_size=18, width=200, height=40, padding=10)
        )
        add_save_box.add(add_section_button)

        #Save Budget Button
        save_button = toga.Button(
            "Save Budget",
            on_press=self.save_budget,
            style=Pack(background_color="#62C54C", padding=(10, 0, 10), width=200, height=50, font_weight="bold", font_size=18)
        )
        add_save_box.add(save_button)

        #Add the add_save_box to the background box
        budget_box.add(add_save_box)

        #For Scrolling
        scroll_container = toga.ScrollContainer(content=budget_box, horizontal=False, style=Pack(padding=10))
        
        self.main_window.content = scroll_container
        self.main_window.show()
        
    def create_budget_section(self, category):
        section_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # title
        section_label = toga.Label(category, style=Pack(font_size=20, font_weight="bold"))
        print(section_label)
        section_box.add(section_label)
        
        # default subsections
        for _ in range(2):
            subsection_box = self.create_budget_subsection()
            section_box.add(subsection_box)
            
        # add subsection button
        add_subsection_button = toga.Button(
                                            "Add Subsection +", on_press=self.add_budget_subsection,
                                            style=Pack(padding=5, font_size=14)
                                            )
        section_box.add(add_subsection_button)
        
        return section_box
        
    # Helper function to create a budget subsection
    def create_budget_subsection(self):
        subsection_box = toga.Box(style=Pack(direction=ROW, padding=5, alignment=CENTER))

        # Subsection Name
        subcategory_input = toga.TextInput(placeholder="Subsection", style=Pack(width=150, padding=(5, 5)))

        # Budget Amount
        amount_input = toga.NumberInput(min=0.00, value=0.00, step=0.01, style=Pack(width=100, padding=(5, 5)))

        # Remaining Budget Label
        remaining_label = toga.Label("$0.00 left", style=Pack(font_size=14, padding_left=10))

        subsection_box.add(subcategory_input)
        subsection_box.add(amount_input)
        subsection_box.add(remaining_label)

        return subsection_box
            
    # Event Handlers
    async def add_budget_section(self, widget):

        #Get the parent and grandparent boxes of the widget
        parent_box = widget.parent
        grandparent_box = parent_box.parent

        grandparent_box.remove(parent_box) #Temporarily remove the parent box from the grandparent box
        new_section = self.create_budget_section("New Section")
        grandparent_box.add(new_section)
        grandparent_box.add(parent_box) #Re-insert the parent box beneath the new section

    async def add_budget_subsection(self, widget):
        parent_box = widget.parent
        parent_box.remove(widget) #Temporarily remove the "Add Subsection +" button
        new_subsection = self.create_budget_subsection()
        parent_box.add(new_subsection)
        parent_box.add(widget) #Re-insert the "Add Subsection +" button
        
    async def save_budget(self, widget):
        # Connect to SQLite database (or create it if it doesn't exist)
        db_path = get_database_path(self)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table if it doesn’t exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            month INTEGER NOT NULL
                        )''')

        # Get selected month
        self.month_names = ["January", "February", "March", "April", "May", "June", "July","August", "September", "October", "November", "December"]
        selected_month = self.month_selection.value
        selected_month_index = self.month_names.index(selected_month)
        
        user_id = 1 # UPDATE THIS LATER FOR LOGIN

        
        # Create Subcategory table in SQL
        cursor.execute('''CREATE TABLE IF NOT EXISTS subcategories (
                            sc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            budget_id INTEGER,
                            amount REAL,
                            category TEXT
                        )''')
        
        budget_we_on = 1 # To be changed when the budget and user ids are implemented

        # Iterate through categories and save them
        for section in self.main_window.content.content.children[2:-1]:
            if isinstance(section, toga.Box):  # Ensure it's a section
                category_label = section.children[0]  # First child is the category label
                category_name = category_label.text #this one is giving an error

                for sub_box in section.children[1:-1]:  # Skip first (category label) and last (Add Subsection button)
                    if isinstance(sub_box, toga.Box) and sub_box.children[0].value != '':  # Ensure it's a subsection and exists

                        subcategory_input = sub_box.children[0]  # First child: Subcategory input
                        amount_input = sub_box.children[1]  # Second child: Amount input

                        subcategory_name = subcategory_input.value
                        amount = amount_input.value
                        
                        print(f"Inserting: subcategory={subcategory_name}, budget_id={budget_we_on}, amount={amount}, category={category_name}")
                        
                        amount = amount_input.value if amount_input.value is not None else 0
                        
                        # Insert data into database
                        cursor.execute("INSERT INTO subcategories (name, budget_id, amount, category) VALUES (?, ?, ?, ?)",
                                        (subcategory_name, budget_we_on, float(amount), category_name))

        cursor.execute("SELECT * FROM subcategories")
        print("Budgets in DB:", cursor.fetchall())
        
        conn.commit()
        conn.close()

        # Redirect back to home screen
        await self.homescreen(widget)

    def empty_box(self):
        return toga.Box(style=Pack(background_color="#C0E4B8", direction=COLUMN, alignment=CENTER))



def main():
    return DegreeDollars()
