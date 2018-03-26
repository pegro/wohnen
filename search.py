import sys
import argparse
import logging

import inberlinwohnen.parser
import inberlinwohnen.scraper
from jsonfile import JsonFile
import config

parser = argparse.ArgumentParser()
parser.add_argument("sites", type=str, nargs='+', help="list of sites to check")
parser.add_argument("--scrape", action="store_true", help="actually scrape")

args = parser.parse_args()

logger = logging.getLogger()
logger.setLevel(config.loglevel)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', "%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

def get_sample(site):
    with open('{}/sample.txt'.format(site), 'r') as f:
        ## html will be a list
        return f.read()

if __name__ == "__main__":
    for site in args.sites:
        logger.debug(site)
        sitem = getattr(sys.modules[__name__], site)
        if args.scrape:
            scraper = getattr(sitem, "scraper")
            html = scraper.scrape()
        else:
            scraper = None
            html = get_sample(site)

        parser = getattr(sitem, "parser")
        flats = parser.parse(html)

        jsonfile = JsonFile.open(config.jsonfile)
        newflats = []
        for flat in flats:
            new = jsonfile.add_item(flat)
            if new:
                newflats.append(flat)

        if jsonfile.new_item_count > 0:
            logging.info("Found {} new flats".format(jsonfile.new_item_count))


        jsonfile.save()
