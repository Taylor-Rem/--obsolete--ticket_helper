from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException
from webdriver_manager.chrome import ChromeDriverManager

from config import username, password, resident_map, management_portal

# boilerplate
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)
wait = WebDriverWait(driver, 10)

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


class InformationNotFoundError(Exception):
    pass


# Helper Functions
def login(username, password):
    try:
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys(username)
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
    except NoSuchElementException:
        pass


def scrape_page():
    try:
        property_element = driver.find_element(
            By.XPATH,
            ticket_property_xpath,
        )
        unit_element = driver.find_element(
            By.XPATH,
            ticket_unit_xpath,
        )
        resident_element = driver.find_element(By.XPATH, ticket_resident_xpath)
        property = property_element.get_attribute("innerHTML")
        unit = unit_element.get_attribute("innerHTML")
        resident = resident_element.get_attribute("innerHTML").strip()
        return property, unit, resident
    except NoSuchElementException:
        raise InformationNotFoundError("Information not found on page")


def new_tab():
    driver.execute_script("window.open('about:blank', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])


def switch_to_primary_tab():
    primary_tab = driver.window_handles[0]
    try:
        current_tab = driver.current_window_handle
        if current_tab != primary_tab:
            driver.close()
    except NoSuchWindowException:
        pass
    driver.switch_to.window(primary_tab)


def nav_to_property(property):
    change_property_link = driver.find_element(
        By.XPATH, "//a[contains(., 'CHANGE PROPERTY')]"
    )
    change_property_link.click()
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    property_link = driver.find_element(By.XPATH, f"//a[contains(., '{property}')]")
    property_link.click()


def nav_to_unit(unit):
    search = driver.find_element(By.NAME, "search_input")
    search.clear()
    search.send_keys(unit)
    search.send_keys(Keys.ENTER)


def open_ledger(unit, resident):
    RM_resident_element = driver.find_element(By.XPATH, resident_xpath)
    RM_resident = RM_resident_element.get_attribute("innerHTML").strip()
    if RM_resident.__contains__(resident):
        try:
            ledger_link = driver.find_element(By.XPATH, ledger_xpath)
            ledger_link.click()
        except NoSuchElementException:
            search_former(unit, resident)
    else:
        search_former(unit, resident)


def search_former(unit, resident):
    former_resident = driver.find_element(By.XPATH, former_button_xpath)
    former_resident.click()
    spacenum = driver.find_element(By.NAME, "ressearch")
    spacenum.clear()
    spacenum.send_keys(resident)
    spacenum.send_keys(Keys.ENTER)
    open_ledger(unit, resident)


# open first page
driver.get(management_portal)
driver.maximize_window()

login(username, password)


# Main Function
def open_ticket():
    switch_to_primary_tab()
    try:
        property, unit, resident = scrape_page()
        new_tab()
        driver.get(resident_map)
        login(username, password)
        nav_to_property(property)
        nav_to_unit(unit)
        open_ledger(unit, resident)
    except InformationNotFoundError as e:
        print(str(e))
