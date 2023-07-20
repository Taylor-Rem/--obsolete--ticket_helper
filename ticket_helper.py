from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException

from webdriver_manager.chrome import ChromeDriverManager

from config import username, password, resident_map, management_portal


class InformationNotFoundError(Exception):
    pass


class TicketHelper:
    # XPATH's
    ticket_list_xpath = "/html/body/div[1]/div[18]/div/main/div/div/div/div[2]/div/div/div/div[1]/table/tbody"
    ticket_property_xpath = "/html/body/div[1]/div[19]/div/main/div/div/div/div/div[2]/div/div/table/tbody/tr[6]/td[2]/strong/a"
    ticket_unit_xpath = "/html/body/div[1]/div[19]/div/main/div/div/div/div/div[2]/div/div/table/tbody/tr[11]/td[2]/a/strong"
    ticket_resident_xpath = "/html/body/div[1]/div[19]/div/main/div/div/div/div/div[2]/div/div/table/tbody/tr[12]/td[2]/a/strong"
    property_xpath = "/html/body/table[2]/tbody/tr[2]/td/table/tbody/tr[1]/td[4]/a"
    ledger_xpath = "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[3]/tbody/tr[2]/td/table/tbody/tr[last()]/td[4]/a[4]"
    resident_xpath = "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[3]/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/a"
    former_button_xpath = "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[3]/tbody/tr[1]/td/table/tbody/tr/td[3]/input[2]"
    former_res_list_xpath = "/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td/table[3]/tbody/tr[2]/td/table/tbody"

    # boilerplate
    def __init__(self):
        options = Options()
        options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        self.wait = WebDriverWait(self.driver, 10)
        self.primary_tab = None

    # Helper Functions
    def login(self, username, password):
        try:
            username_input = self.driver.find_element(By.NAME, "username")
            password_input = self.driver.find_element(By.NAME, "password")
            username_input.send_keys(username)
            password_input.send_keys(password)
            password_input.send_keys(Keys.ENTER)
        except NoSuchElementException:
            pass

    def scrape_page(self):
        try:
            property_element = self.driver.find_element(
                By.XPATH,
                self.ticket_property_xpath,
            )
            unit_element = self.driver.find_element(
                By.XPATH,
                self.ticket_unit_xpath,
            )
            resident_element = self.driver.find_element(
                By.XPATH, self.ticket_resident_xpath
            )
            property = property_element.get_attribute("innerHTML")
            unit = unit_element.get_attribute("innerHTML")
            resident = resident_element.get_attribute("innerHTML").strip()
            return property, unit, resident
        except NoSuchElementException:
            try:
                property_element = self.driver.find_element(
                    By.XPATH,
                    self.ticket_property_xpath,
                )
                property = property_element.get_attribute("innerHTML")

                resident_element = self.driver.find_element(
                    By.XPATH, self.ticket_resident_xpath
                )
                resident = resident_element.get_attribute("innerHTML").strip()
                return property, resident, resident
            except NoSuchElementException:
                try:
                    property_element = self.driver.find_element(
                        By.XPATH,
                        self.ticket_property_xpath,
                    )
                    property = property_element.get_attribute("innerHTML")
                    unit_element = self.driver.find_element(
                        By.XPATH,
                        self.ticket_unit_xpath,
                    )
                    unit = unit_element.get_attribute("innerHTML")
                    return property, unit, unit
                except NoSuchElementException:
                    property_element = self.driver.find_element(
                        By.XPATH,
                        self.ticket_property_xpath,
                    )
                    property = property_element.get_attribute("innerHTML")
                    print("Only property name found")
                    return property, None, None
            except Exception as e:
                print("An error ocurred:", e)
                return None, None, None

    def new_tab(self):
        self.driver.execute_script("window.open('about:blank', '_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def switch_to_primary_tab(self):
        if self.primary_tab is None:
            self.primary_tab = self.driver.window_handles[0]
        else:
            try:
                current_tab = self.driver.current_window_handle
                if current_tab != self.primary_tab:
                    self.driver.close()
            except NoSuchWindowException:
                pass
        self.driver.switch_to.window(self.primary_tab)

    def nav_to_property(self, property):
        change_property_link = self.driver.find_element(
            By.XPATH, "//a[contains(., 'CHANGE PROPERTY')]"
        )
        change_property_link.click()
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        property_link = self.driver.find_element(
            By.XPATH, f"//a[contains(., '{property}')]"
        )
        property_link.click()

    def nav_to_unit(self, unit):
        search = self.driver.find_element(By.NAME, "search_input")
        search.clear()
        search.send_keys(unit)
        search.send_keys(Keys.ENTER)

    def open_ledger(self, unit, resident):
        RM_resident_element = self.driver.find_element(By.XPATH, self.resident_xpath)
        RM_resident = RM_resident_element.get_attribute("innerHTML").strip()
        if resident in RM_resident:
            try:
                ledger_link = self.driver.find_element(By.XPATH, self.ledger_xpath)
                ledger_link.click()
            except NoSuchElementException:
                self.search_former(unit, resident)
        else:
            self.search_former(unit, resident)

    def search_former(self, unit, resident):
        former_resident = self.driver.find_element(By.XPATH, self.former_button_xpath)
        former_resident.click()
        spacenum = self.driver.find_element(By.NAME, "ressearch")
        spacenum.clear()
        spacenum.send_keys(resident)
        spacenum.send_keys(Keys.ENTER)
        self.open_ledger(unit, resident)

    # Main Function
    def open_ticket(self):
        self.switch_to_primary_tab()
        try:
            property, unit, resident = self.scrape_page()
            self.new_tab()
            self.driver.get(resident_map)
            self.login(username, password)
            self.nav_to_property(property)
            if unit != None:
                self.nav_to_unit(unit)
                self.open_ledger(unit, resident)
        except InformationNotFoundError as e:
            print(str(e))
