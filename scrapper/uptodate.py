#!/usr/bin/env python
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.database import insert_references_as_citations

driver = webdriver.Firefox()

link = "https://www.uptodate.com/contents/noncardiogenic-pulmonary-edema"
link += "#references"

try:
    driver.get(link)
    wait = WebDriverWait(driver, timeout=20)
    wait.until(EC.visibility_of_element_located((By.ID, "reference")))
    references = driver.find_element(by=By.ID, value="reference")
    insert_references_as_citations(references.text.splitlines())
except Exception as e:
    logging.error(e)
finally:
    driver.quit()
