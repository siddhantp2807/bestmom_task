from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import datetime

from time import sleep
import re, sys, regex


class Scraper :

    def __init__(self, url="https://www.1mg.com/drugs/dolo-650-tablet-74467") -> None:

        self.options = Options()
        self.options.add_argument("--disable-notifications")
        
        self.driver = webdriver.Chrome(options=self.options)

        self.driver.get(url)

        self.data = {}
        sleep(5)
    
    def filter_amt(self, text) :
        nums = re.findall(r'[0-9]+[a-zA-Z%/]{0,}',text)
        return nums

    def filter_category(self, text) :
        reqd = re.findall(r'[a-zA-Z/]+', text)
        return reqd[-1]
    
    def filter_brand(self, text) :
        reqd = re.findall(r'[a-zA-Z/\(\)]+', text)
        return reqd[0]

    def filter_prices(self, text) :
    
        num = re.compile(r'\d*[.,]?\d*')
        chars = re.compile(r'[A-Za-z]+')
        currency = regex.findall(r'\p{Sc}', text)
        price = [i for i in num.findall(text) if i != ''][0]

        unit = " ".join(chars.findall(text))
        return price, unit, currency[0]
    
    def close_popups(self) :

        element_present_class = ''
        sleep(30)

        try :
            element_present_class = WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class^='style__wrapper']"))).get_attribute("class")
        except :
            print("Could not find element!")
            sys.exit(0)

        print(f"Class: {element_present_class}")
        get_rid_script = f"""let it = document.getElementsByClassName('{element_present_class}')[0];\nit.style.display = 'none';"""
        enable_scroll = """let d = document.getElementsByTagName('body')[0];\nd.style.overflowY = 'auto';"""

        self.driver.execute_script(get_rid_script)
        sleep(2)

        self.driver.find_element_by_css_selector("div[class^='UpdateCityModal__cancel-btn']").click()
        sleep(2)

        self.driver.execute_script(enable_scroll)
        sleep(2)

    def get_drug(self) :

        sleep(3)

        drug_name = self.driver.find_element_by_css_selector("h1").text
        drug_data = [i.get_attribute("text") for i in self.driver.find_elements_by_css_selector(".saltInfo a")]
        active_drug = ""
        synonyms = []

        if len(drug_data) == 1 :
            active_drug = [drug.strip() for drug in drug_data[0].split("+")]

        elif len(drug_data) == 2 :
            active_drug = [drug.strip() for drug in drug_data[0].split("+")]
            synonyms = drug_data[1].split(",")
        
        self.data["name"] = {
            "brand" : self.filter_brand(drug_name),
            "dosage_form" : self.filter_category(drug_name),
            "number_in_brand" : self.filter_amt(drug_name)
        }

        self.data["active_drug"] = active_drug

        self.data["synonyms"] = synonyms
    
    def get_current_brand(self) :

        sleep(5)

        price_box = self.driver.find_elements_by_css_selector("div[class^='PriceBoxPlanOption__flex']")[0]
        price = price_box.find_element_by_css_selector("span[class^='PriceBoxPlanOption__offer-price']").text
        quantity = self.driver.find_element_by_css_selector("div[class^='DrugPriceBox__quantity']").text

        self.data["cost"] = {
            "price" : price,
            "quantity" : quantity
        }

    def get_brands(self) :
        
        sleep(5)

        brand_data = []

        brand_name = [i.text for i in self.driver.find_elements_by_css_selector("div[class^='row SubstituteItem__item'] a div")]
        brand_price = [j.text for j in self.driver.find_elements_by_css_selector("div[class^='row SubstituteItem__item'] div[class^='SubstituteItem__unit-price']")]

        for key, value in list(zip(brand_name, brand_price)) :
            
            brand_data.append({
                "name" : key,
                "price" : self.filter_prices(value)[0],
                "unit" : self.filter_prices(value)[1],
                "currency" : self.filter_prices(value)[2]
            })
        
        self.data["alternate_brands"] = brand_data

    def get_side_effects(self) :
        sleep(3)

        effects = self.driver.find_elements_by_css_selector("div[class^='DrugOverview__list-container'] ul li")

        text_effect = [i.text for i in effects]

        self.data["side_effects"] = text_effect

    def finish(self) :
        self.driver.quit()

    def combine_all(self) :

        self.get_drug()
        self.get_current_brand()
        self.get_brands()
        self.get_side_effects()
        self.finish()
        self.data["scraped_at"] = datetime.datetime.now().timestamp()

        return self.data
    
    
        

