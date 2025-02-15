"""
A budgeting application for undergraduate and graduate college students
"""

import toga
import httpx
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class DegreeDollars(toga.App):
    def startup(self): #Define the app's behavior when it is initially opened
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """

        main_box = toga.Box(style=Pack(background_color=("#C0E4B8"), direction=COLUMN)) #The box that opens upon startup
        logo_img = toga.Image("DegreeDollarsLogo.png") #imports the logo
        # it requires a ImageView object to see the image
        view = toga.ImageView(logo_img, style=Pack(padding=(207, 22, 0, 22), width=350, height=140))
        main_box.add(view)
        button = toga.Button(
            "View My Budgets",
            on_press=self.button_hi,
            style=Pack(padding=(33, 50), width=302, height=56)
        )
        main_box.add(button)

        self.main_window = toga.MainWindow(title=self.formal_name) #Window in which box is displayed
        self.main_window.content = main_box
        self.main_window.show()

    async def button_hi(self, widget):
        await self.main_window.dialog(
            toga.InfoDialog(
                "Hey you pressed my button!",
                "Wowww"
            )
        )

def main():
    return DegreeDollars()
