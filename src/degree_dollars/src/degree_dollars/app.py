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
        background = toga.Box(style=Pack(background_color=("#C0E4B8"), direction=COLUMN, alignment=CENTER))
        
        #Import the navigation bar icons (for when Home Screen is active)
        profile_img = toga.Image("Profile.png")
        activehome_img = toga.Image("Home (Active).png") #Active version of "Home" button
        addexpense_img = toga.Image("Add Expense.png")
        loancalc_img = toga.Image("Loan Calculation.png")

        profile_view = toga.ImageView(profile_img, style=Pack(width=40, height=40))

        nav_bar = toga.Box(style=Pack(background_color=("#62C54C"), direction=ROW, height=62))

        nav_bar.add(profile_view)
        
        background.add(nav_bar)

        self.main_window.content = background
        self.main_window.show()

def main():
    return DegreeDollars()
