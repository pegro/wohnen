#coding: utf-8

import json
import logging
import re
import datetime

from urllib.parse import urljoin, quote
import urllib
from lxml import html

logger = logging.getLogger(__name__)

def parse(html_input):
    '''<div class="fc_col span_flatcolumn" id="cflat_1233429" >
        <div style="position:relative;"><a class="flatlink" id="flat_1233429"></a></div>
          <div class="section group">
            <div class="col span_1_of_3">
              <figure class="flat-image wide" style="background-image:url(https://inberlinwohnen.de/wp-content/uploads/flats/v2-degewo-121569623861ed9e3342293_20220123192803-300x300.jpg);">
                <img src="https://inberlinwohnen.de/wp-content/themes/ibw/images/square-image.gif" alt="" />
              </figure>
              <a title="Die detailierte Wohnungsanzeige öffnet in einem neuen Fenster" class="org-but" href="/gpgf_W1100.11902.0148-0108.html" target="_blank">Alle Details</a>
              <div class="iconleiste">
                <a title="Balkon/Terasse" class="icon balkon_loggia_terrasse nohand" href=""></a>
                <a title="Aufzug" class="icon aufzug nohand" href=""></a>
                <a title="Wohnberechtigungsschein" class="icon wbs nohand" href=""></a>
              </div>
            </div>
            <div class="col span_2_of_3 flatprofil">
              <h3>Wohnen im Grünen für 55+</h3>
              <p class="adresse">
                <a title="Auf Karte anzeigen" class="map-but" href="#" onclick="openOverlay('nmap-1233429','de'); return false;">Horstwalder Straße 5A, Lichtenrade</a>
              </p>
              <div class="maincriteria">
                <dl>
                  <dt>305,01 &euro;</dt>
                  <dd>Kaltmiete</dd>
                </dl>
                <dl>
                  <dt>40,08 m²</dt>
                  <dd>Wohnfläche</dd>
                </dl>
                <dl>
                  <dt>1.00</dt>
                  <dd>Zimmer</dd>
                </dl>
              </div>
              <div class="addcriteria">
                <dl>
                  <dd>Nebenkosten:</dd>
                  <dt>106,21 &euro;</dt>
                </dl>
                <dl>
                  <dd>Gesamtmiete:</dd>
                  <dt>411,22 &euro;</dt>
                </dl>
                <dl>
                  <dd>Bezugsfertig ab:</dd>
                  <dt>sofort</dt>
                </dl>
                <dl>
                  <dd>Etage:</dd>
                  <dt>1 (von insg. 4)</dt>
                </dl>
                <dl>
                  <dd>Badezimmer:</dd>
                  <dt>1</dt>
                </dl>
                <dl>
                  <dd>Baujahr:</dd>
                  <dt>1977</dt>
                </dl>
                <dl>
                  <dd><abbr title="Wohnberechtigungsschein">WBS</abbr>:</dd>
                  <dt>erforderlich</dt>
                </dl>
              </div>
              <span class="hackerl">Balkon/Terrasse</span>
              <span class="hackerl">Aufzug</span>
              <p>
                <small>Eine Wohnung der</small>
                <img src="https://inberlinwohnen.de/wp-content/themes/ibw/images/logos/degewo-small-grey.jpg" style="width:100%; max-width:100px; line-height:10px; vertical-align:middle;" alt="" />
              </p>
            </div>
          </div>
        </div>
    '''
    base_url = "https://inberlinwohnen.de/"

    results = json.loads(html_input)

    # get location markers first
    markers = {}
    if 'addmarkers' in results:
      marker_list = json.loads(results['addmarkers'].replace("'",'"'))
      for marker in marker_list:
        marker_id_s = re.search('showWFflat\(0,(\d+)\)', marker[2])
        if marker_id_s:
          marker_id = marker_id_s.group(1)
          markers[marker_id] = {
            'lat': marker[0],
            'long': marker[1]
          }

    # parse results
    tree = html.fromstring(results['searchresults'])
    all_flats = tree.xpath("//div[contains(@id,'flat_')]")

    logger.info("Will parse {} flats".format(len(all_flats)))

    for flat in all_flats:
        # Titel, ID und Link
        title = flat.xpath(".//h3")[0].text_content().strip()
        id = flat.xpath(".//a[contains(@id,'flat_')]/@id")[0].replace('flat_','')
        link = flat.xpath(".//a[contains(@title,'Die detailierte')]/@href")[0]

        # Adresse
        adresse = flat.xpath(".//a[contains(@title,'Auf Karte anzeigen')]")[0].text_content().strip().split(',')
        addr = adresse[0]
        kiez = adresse[1].strip() if len(adresse) > 1 else ''

        # Bild
        image = flat.xpath(".//figure/@style")[0]
        image_url = None
        if image:
            image_url_s = re.search('background-image:url\((.*)\)', image)
            if image_url_s is not None:
                image_url = image_url_s.group(1)

        # Vermieter
        landlord_str = flat.xpath(".//img[contains(@src,'small-grey.jpg')]/@src")[0]
        landlord_s = re.search('logos/([a-zA-Z]+)-small', landlord_str)
        landlord = ''
        if landlord_s:
          landlord = landlord_s.group(1).capitalize()

        # Eigenschaften
        all_props = flat.xpath('.//dl')
        props = {}
        for prop in all_props:
          prop_key = prop.xpath(".//dd")[0].text_content().replace(':','').strip()

          prop_val_el = prop.xpath(".//dt")[0]
          prop_val = ''.join([prop_val_el.text] + [html.tostring(el).decode('utf-8') for el in prop_val_el])
          prop_val = prop_val.replace('<br>',' ')

          props[prop_key] = prop_val

        # Besonderheiten
        features = []
        all_features = flat.xpath(".//span[contains(@class, 'hackerl')]")
        for feature in all_features:
          features.append(feature.text_content())

        yield {
            'id': id,
            'date_found': datetime.datetime.now().strftime('%d.%m.%Y %H:%M'),
            'title': title,
            'addr': addr,
            'kiez': kiez if len(kiez) > 0 else '-',
            'pos': markers[id] if id in markers else None,
            'link': quote(urljoin(base_url, link), safe=":/"),
            'image': quote(image_url, safe=':/'),
            'landlord': landlord,
            'properties': props,
            'features': features
        }
