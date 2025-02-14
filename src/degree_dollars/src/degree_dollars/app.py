"""
A budgeting application for undergraduate and graduate college students
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class DegreeDollars(toga.App):
    def startup(self): #Define the app's behavior when it is initially opened
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box(style=Pack(background_color=("#C0E4B8"))) #The box that opens upon startup

        self.main_window = toga.MainWindow(title=self.formal_name) #Window in which box is displayed
        self.main_window.content = main_box
        self.main_window.show()


def main():
    return DegreeDollars()
