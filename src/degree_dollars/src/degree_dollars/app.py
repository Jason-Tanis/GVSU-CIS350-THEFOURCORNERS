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

        #Box for background
        bg_box = toga.Box(style=Pack(background_color=("#C0E4B8"), direction=COLUMN))

        #Box for navigation bar
        navbar = toga.Box(style=Pack(background_color=("#62C54C"), direction=COLUMN, alignment=CENTER))
        
        #Import the navigation bar icons (for when Home Screen is active)
        profile = toga.Icon("Profile")
        home = toga.Icon("Home")
        loancalc = toga.Icon("Loan Calculation")
        addexpense = toga.Icon("Add Expense.png")

        #Create buttons for each icon
        profile_btn = toga.Button(icon = profile, style=Pack(width=45, height=45, padding=(6, 44, 6, 31)))
        home_btn = toga.Button(icon = home, enabled = False, style=Pack(width=45, height=45, padding=(6, 44, 6, 0))) #You cannot press the home button while the Home Screen is open (i.e., enabled = False)
        loancalc_btn = toga.Button(icon = loancalc, style=Pack(width=45, height=45, padding=(6, 44, 6, 0)))
        addexpense_btn = toga.Button(icon = addexpense, style=Pack(width=45, height=45, padding=(6, 31, 6, 0)))

        #Add the icons to the navigation bar
        icons = toga.Box(style=Pack(background_color=("#62C54C"), direction=ROW, alignment=CENTER, height=62))
        icons.add(profile_btn, home_btn, loancalc_btn, addexpense_btn)
        navbar.add(icons)

        #Add the navigation bar to the background box
        bg_box.add(navbar)

        #Make the Home Screen a ScrollContainer (so it will have a scroll bar when it has more content
        #than can be displayed in the window)
        background = toga.ScrollContainer(horizontal = False, content = bg_box) #Do not permit horizontal scrolling

        #Display the homescreen contents
        self.main_window.content = background
        self.main_window.show()

def main():
    return DegreeDollars()
