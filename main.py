from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from config import username, password, management_portal
from ticket_helper import TicketHelper


class TicketApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ticket Management")

        # Create TicketHelper instance
        self.helper = TicketHelper()

        # Set up the main window layout
        layout = QVBoxLayout()
        self.label = QLabel("Ticket Helper")
        layout.addWidget(self.label)

        self.button_ticket = QPushButton("Open Ticket")
        self.button_ticket.clicked.connect(self.open_ticket)
        layout.addWidget(self.button_ticket)

        self.button_exit = QPushButton("Exit")
        self.button_exit.clicked.connect(self.close_windows)
        layout.addWidget(self.button_exit)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.helper.driver.get(management_portal)
        self.helper.driver.maximize_window()
        self.helper.login(username, password)

    def open_ticket(self):
        self.helper.open_ticket()

    def close_windows(self):
        self.helper.driver.quit()
        self.close()


if __name__ == "__main__":
    app = QApplication([])
    window = TicketApp()
    window.show()
    app.exec_()
