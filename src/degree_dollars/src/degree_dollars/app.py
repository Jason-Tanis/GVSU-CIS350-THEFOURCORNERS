"""
A budgeting application for undergraduate and graduate college students
"""

import toga
import httpx
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

class DegreeDollars(toga.App):
    def startup(self): #Define the app's behavior when it is initially opened
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """

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
            style=Pack(background_color="#62C54C", padding=(10, 0, 10),
            width=250, height=50, font_weight="bold", font_size=16)
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
        monthfield_label = toga.Label("Indicate current month", style=Pack(color="#000000", font_size=14))
        monthfield = toga.NumberInput(min = 1, max = 12, value = 1, step = 1)
        month_box.add(monthfield_label, monthfield)
        spacer.add(month_box)
        budget_box.add(spacer)

        #Predefined categories (just to fill in space)
        categories = ["Food", "Transportation", "Education", "Entertainment"]
        for category in categories:
            category_box = toga.Box(style=Pack(background_color="#C0E4B8", direction=COLUMN, padding=(10, 0)))
            label = toga.Label(category, style=Pack(background_color="#C0E4B8", color="#000000", font_size=20, font_weight="bold", padding=(5, 0)))
            budget_box.add(label)

            #Input fields
            subcategory_input = toga.TextInput(placeholder="Subcategory", style=Pack(width=200, padding=(5, 5)))
            category_box.add(subcategory_input)

            amount_input = toga.NumberInput(
                    min = 0, value = 0, step = 0.01,
                    style=Pack(width=120, padding=(5, 5)))

            category_box.add(amount_input)

            budget_box.add(category_box)

        #Save Budget Button
        save_button = toga.Button(
            "Save Budget",
            on_press=self.homescreen,
            style=Pack(background_color="#62C54C", padding=(10, 0, 10), width=200, height=50, font_weight="bold", font_size=16)
        )
        budget_box.add(save_button)

        #For Scrolling
        scroll_container = toga.ScrollContainer(content=budget_box, horizontal=False, style=Pack(padding=10))
        
        self.main_window.content = scroll_container
        self.main_window.show()

    def empty_box(self):
        return toga.Box(style=Pack(background_color="#C0E4B8", direction=COLUMN, alignment=CENTER))

def main():
    return DegreeDollars()
