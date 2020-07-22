from selenium import webdriver
import sys

# Init driver
driver = webdriver.Chrome("./chromedriver")
print("Beginning tests...\n")

# Open main
driver.get("http://localhost:5000/")

# Check ai button
driver.find_element_by_id("ai_button").click()
resp = driver.find_element_by_id("ai_resp").text
print("AI Test:\t\t", end="")
if resp == "Buy Bitcoin - We going to the moon!":
    print("Passed")
else:
    print("Failed")
    print("\nExiting...")
    driver.close()
    sys.exit(1)

# Check client button
driver.find_element_by_id("client_button").click()
resp = driver.find_element_by_id("clients_resp").text
print("Client Test:\t\t", end="")
if resp == "Hugh\nTina\nKevin\nJiawei":
    print("Passed")
else:
    print("Failed")
    print("\nExiting...")
    driver.close()
    sys.exit(1)

# Check portfolio button
driver.find_element_by_id("portfolio_button").click()
resp = driver.find_element_by_id("portfolio_resp").text
print("Portfolio Test:\t\t", end="")
if resp == "WOW : 50\nCBA : 70\nWTF : 150":
    print("Passed")
else:
    print("Failed")
    print("\nExiting...")
    driver.close()
    sys.exit(1)

# Close webpage
print("\nAll tests passed")
driver.close()
