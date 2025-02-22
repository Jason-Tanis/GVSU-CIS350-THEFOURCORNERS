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
        view = toga.ImageView(logo_img, style=Pack(padding=(200, 0, 0), width=300, height=150))
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

        #Create boxes for each navigation bar tab (currently, they are all empty boxes)
        profile = self.empty_box()
        home    = self.empty_box()
        loan    = self.empty_box()
        addexp  = self.empty_box()

        #Create navigation bar as an OptionContainer
        navbar = toga.OptionContainer(
                content = [
                    toga.OptionItem("Profile", profile, icon = toga.Icon("Profile.png")),
                    toga.OptionItem("Home", home, icon = toga.Icon("Home.png")),
                    toga.OptionItem("Loan Planner", loan, icon = toga.Icon("Loan Calculation.png")),
                    toga.OptionItem("Add Expense", addexp, icon = toga.Icon("Add Expense.png"))
                ]
        )

        #Make "Home" the currently open tab
        navbar.current_tab = "Home"

        #Display the homescreen contents
        self.main_window.content = navbar
        self.main_window.show()

    def empty_box(self):
        empty_box = toga.Box(style=Pack(background_color = ("#C0E4B8"), direction=COLUMN, alignment=CENTER))
        return empty_box

def main():
    return DegreeDollars()
