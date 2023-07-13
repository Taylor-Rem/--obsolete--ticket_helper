from config import username, password, management_portal
from ticket_helper import TicketHelper

if __name__ == "__main__":
    helper = TicketHelper()
    helper.driver.get(management_portal)
    helper.driver.maximize_window()
    helper.login(username, password)
    while True:
        user_input = input(
            """
            Press 1 or nothing to open new ticket
            Press 2 to Exit
            """
        )
        if user_input is None or user_input == "":
            user_input = 1
        user_input = int(user_input)
        if user_input == 1:
            helper.open_ticket()
        elif user_input == 2:
            break
        else:
            print("Please enter either 1 or 2")
    helper.driver.quit()
