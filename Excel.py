import pandas as pd
import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

EXCEL_FILE = "option.xlsx"
COLUMN_NAME = "Display Name"

URL = (
    "https://elements.symplectic.org/"
    "underlyingfield.html?"
)


DRY_RUN = False

# Read Excel file
df = pd.read_excel(EXCEL_FILE, dtype=str)

if COLUMN_NAME not in df.columns:
    raise ValueError(
        f"Excel must contain a '{COLUMN_NAME}' column."
    )

options = (
    df[COLUMN_NAME]
    .dropna()
    .astype(str)
    .str.strip()
)

options = list(dict.fromkeys(
    option for option in options if option
))

print(f"Loaded {len(options)} unique options.")

# Open browser

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

results = []

try:
    driver.get(URL)

    input(
        "\nLog in to Symplectic Elements, "
        "open the field configuration page, "
        "then press ENTER..."
    )


    def get_existing_options():

        existing = set()

        elements = driver.find_elements(
            By.XPATH,
            "//*[contains(normalize-space(.), 'Display name:')]"
        )

        for element in elements:

            text = element.text.strip()

            match = re.search(
                r"Display name:\s*(.+)",
                text
            )

            if match:
                existing.add(
                    match.group(1).strip().casefold()
                )

        return existing


    def add_option(option_name):

        # Click Add new option
        add_button = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'button[data-qa-id="add-item"]'
            ))
        )

        add_button.click()

        # Find Display name input
        display_input = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                'input[data-qa-id="display-name-field"]'
            ))
        )

        # Enter name from Excel
        display_input.clear()
        display_input.send_keys(option_name)

        print(f"Entered: {option_name}")

        # Find Save button
        save_button = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'button[data-qa-id="save"]'
            ))
        )

        save_button.click()

        print(f"Clicked Save for: {option_name}")


        # Wait until Add choice dialog closes
        wait.until(
            EC.invisibility_of_element_located((
                By.CSS_SELECTOR,
                'input[data-qa-id="display-name-field"]'
            ))
        )

        print(f"Modal closed for: {option_name}")

        # Verify option appears in the list
        wait.until(
            lambda d: (
                option_name.casefold()
                in get_existing_options()
            )
        )

    existing_options = get_existing_options()

    print(
        f"Detected {len(existing_options)} "
        "existing options."
    )

    for index, option in enumerate(options, start=1):

        print(f"\n[{index}/{len(options)}] {option}")

        if option.casefold() in existing_options:

            print("SKIPPED: Already exists")

            results.append({
                "Display Name": option,
                "Status": "Already Exists"
            })

            continue

        if DRY_RUN:

            print("DRY RUN: Would add")

            results.append({
                "Display Name": option,
                "Status": "Dry Run"
            })

            continue

        try:

            add_option(option)

            existing_options.add(option.casefold())

            print("SUCCESS: Added")

            results.append({
                "Display Name": option,
                "Status": "Added"
            })

            time.sleep(0.5)

        except Exception as e:

            print(f"ERROR: {e}")

            results.append({
                "Display Name": option,
                "Status": "Unverified - Check Manually"
            })

            # Stop to avoid duplicate submissions
            break

finally:

    # Double check using excel

    results_df = pd.DataFrame(
        results,
        columns=["Display Name", "Status"]
    )

    results_df.to_excel(
        "results.xlsx",
        index=False
    )

    print("\n================================")
    print("PROCESS FINISHED")
    print("================================")

    if not results_df.empty:
        print(results_df["Status"].value_counts())

    print("\nReport: symplectic_results.xlsx")

    input("\nPress ENTER to close browser...")

    driver.quit()
