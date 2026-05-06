from scraper_manager import OlxScraper
from dotenv import load_dotenv

url = "https://www.olx.ua/uk/nedvizhimost/kvartiry/prodazha-kvartir/q-%D0%BA%D0%B2%D0%B0%D1%80%D1%82%D0%B8%D1%80%D0%B0-%D0%BA%D0%B0%D0%BC'%D1%8F%D0%BD%D0%B5%D1%86%D1%8C-%D0%BF%D0%BE%D0%B4%D1%96%D0%BB%D1%8C%D1%8C%D0%BA%D0%B8%D0%B9/?currency=UAH&search%5Bfilter_float_total_area:from%5D=40&search%5Bfilter_float_total_area:to%5D=200&search%5Bfilter_enum_number_of_rooms_string%5D%5B0%5D=dvuhkomnatnye&search%5Bfilter_enum_number_of_rooms_string%5D%5B1%5D=trehkomnatnye&search%5Bfilter_enum_number_of_rooms_string%5D%5B2%5D=chetyrehkomnatnye&search%5Bfilter_enum_apartments_object_type%5D%5B0%5D=secondary_market"

scraper = OlxScraper()
print("Scraping urls...")
ads_urls = scraper.scrape_ads_urls(url)
print(f"Found {len(ads_urls)} ads")
if ads_urls:
    print(f"First ad url: {list(ads_urls)[0]}")
    data = scraper.get_ad_data(list(ads_urls)[0])
    print(f"Ad data: {data}")
