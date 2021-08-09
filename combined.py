from db_manager import Manager
import json
from script import Scraper

scrape = Scraper()
scrape.close_popups()
data = scrape.combine_all()

# To save data to JSON file: 
# json.dump(data, open("data.json", "w"))

manager = Manager("bestmom", "scraped")
manager.add_record(data)
