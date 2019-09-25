from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import datetime
from csv import DictWriter
from platform import system
import os

os.system("cls||clear")
print("=== Dodge Challenger Data Collection ===\n")
print("Initializing...")

# Set driver options
options = Options()
options.headless = True
# Set driver capabilities
capabilities = DesiredCapabilities().FIREFOX
capabilities["pageLoadStrategy"] = "eager"
# Load firefox webdriver
executable_path = "resources/geckodriver.exe" if system() == "Windows" else "resources/geckodriver"
driver = webdriver.Firefox(
	options=options,
	desired_capabilities=capabilities,
	executable_path=executable_path
)

# Load URL for all dodge challenger listings
search_page = "https://www.autotrader.ca/cars/dodge/challenger/on/toronto/"
driver.get(search_page)

# list of car listings
links = []
# Prepare a data object to fill up and export to CSV
car_data = []

# Store all search result URLs 
results = driver.find_elements_by_css_selector(".result-item-inner")
for result in results:
	link = result.find_element_by_css_selector("h2 a").get_attribute("href")
	links.append(link)

# Go to each URL and gather data for the car
for i, link in enumerate(links):
	print("Collecting data for car #{0}".format(i + 1))
	driver.get(link)
	specs = driver.find_elements_by_css_selector("#vdp-specs-content tbody tr:not(:last-of-type)")
	car = {}
	car["Name"] = driver.find_element_by_css_selector(".vdp-hero-title").text.strip()
	car["Price"] = driver.execute_script("return document.querySelector('.vdp-hero-price').innerText.trim()")
	car["Link"] = link
	
	for spec in specs:
		key = spec.find_element_by_css_selector("th").text.strip()
		value = spec.find_element_by_css_selector("td").text.strip()
		car[key.capitalize()] = value

	car_data.append(car)

# Close web driver and remove log file
driver.close()
os.remove("geckodriver.log")

# Write data into a spreadsheet file
print("Generating Spreadsheet")
time = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
filename = "spreadsheets/car-data-{0}.csv".format(time)
with open(filename, "w") as csvfile:
	fieldnames = car_data[0].keys()
	writer = DictWriter(csvfile, fieldnames=fieldnames)

	writer.writeheader()
	for car in car_data:
		writer.writerow(car)

print("Done!\n")

# Open spreadsheet in default program
os.startfile(filename) if system() == "Windows" else os.system("open " + filename)
