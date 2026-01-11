import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys
import re 
import os

# --- KONFIGURACJA ---
def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.timeouts = { 'pageLoad': 30000 }
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def normalize_name(name):
    if not isinstance(name, str): return ""
    cleaned = re.sub(r'[^\w\s]', '', name, flags=re.UNICODE) 
    normalized = cleaned.strip().lower()
    return re.sub(r'\s+', ' ', normalized)

# --- DANE ---
URL_LOGIN = "https://easy-plu.knowledge-hero.com/login"
EMAIL_SELECTOR = "#user-email-login"
PASS_SELECTOR = "#password-login"

# Selektory nawigacji
BTN_TEST_PLU = "#dashboard_category_knowledge_level"
BTN_ALL_ARTICLES = "#execute-all-articles"
BTN_STEP_2_GROUP = "#app > div > div > div > div > div > div.container-small.learn-mode-step2-container > div.learn-mode-step2-product-groups-wrapper.row.gx-4.gy-4.mb-2 > div.col-12 > div > div > div"

# Selektory testu
PLU_INPUT = "input[data-testid='plu-number-input']"
PRODUCT_NAME_XPATH = "//div[contains(@class, 'product-name')]//h1"
LOGOUT_BTN = "#logout > svg"

# Przycisk końca testu (do wykrycia, że test się skończył)
BTN_TRY_AGAIN = "#app > div > div > div > div > div.tw\\:bg-card.tw\\:text-card-foreground.tw\\:flex.tw\\:flex-col.tw\\:gap-6.tw\\:rounded-xl.tw\\:border.tw\\:py-6.tw\\:shadow-sm.tw\\:border-gray-300.tw\\:w-full.tw\\:max-w-xl.tw\\:text-center > div.tw\\:items-center.tw\\:\\[\\.border-t\\]\\:pt-6.tw\\:flex.tw\\:flex-col.tw\\:md\\:flex-row.tw\\:justify-center.tw\\:gap-4.tw\\:max-w-lg.tw\\:mt-6.tw\\:mx-auto.tw\\:px-4.tw\\:w-full > button"

# --- PEŁNA LISTA KONT ---
ACCOUNTS = [
    # STARE KONTA (22)
    {"u": "ziembek", "p": "Lidl2150!"},
    {"u": "Darkcarlos24", "p": "Lidl1698#"},
    {"u": "Jadwiga1", "p": "Lidl1698!"},
    {"u": "Luki70", "p": "kASIECZEK01!"},
    {"u": "Matimati", "p": "Matimati12!"},
    {"u": "Senpai:#", "p": "Senpai:3"},
    {"u": "Sklep1698", "p": "Sklep1698!"},
    {"u": "Sklep1698!", "p": "Sklep1698!"},
    {"u": "Sklep1698!!", "p": "Sklep1698!"},
    {"u": "Sklep1698!!!", "p": "Sklep1698!"},
    {"u": "Sklep1698!!!!", "p": "Sklep1698!"},
    {"u": "piotrrrrr", "p": "Lidl1698!"},
    {"u": "ArCzar", "p": "Lidl1698!"},
    {"u": "janoslaf", "p": "20Dwudziesty#"},
    {"u": "Łukaniu", "p": "Kasia0606#"},
    {"u": "justynka2", "p": "Lidl1698!"},
    {"u": "Lidl1698", "p": "Sklep1698!"},
    {"u": "GrzPasz", "p": "Lidl1698!"},
    {"u": "AneWojc", "p": "Lidl1698!"},
    {"u": "Aguniunia", "p": "Sklep1698!"},
    {"u": "kwaniewski35@gmail.com", "p": "Lidl1698!"},
    {"u": "AsiaDw", "p": "Lidl1698!"},

    # NOWE KONTA (20)
    {"u": "Donataa", "p": "Rydygiera*1"},
    {"u": "Mimasze", "p": "Rydygiera*1"},
    {"u": "Dj Dante", "p": "Rydygiera*1"},
    {"u": "MarBur2150", "p": "Rydygiera*1"},
    {"u": "RGryz", "p": "Rydygiera*1"},
    {"u": "EGrzeszyk", "p": "Rydygiera*1"},
    {"u": "KKrzyżanowski", "p": "Rydygiera*1"},
    {"u": "R.K.-2150", "p": "Rydygiera*1"},
    {"u": "Paulina00", "p": "Rydygiera*1"},
    {"u": "Dominik1981", "p": "Rydygiera*1"},
    {"u": "Barbara_1980", "p": "Rydygiera*1"},
    {"u": "EwaSkot", "p": "Rydygiera*1"},
    {"u": "TomekG", "p": "Rydygiera*1"},
    {"u": "Fineasz", "p": "Rydygiera*1"},
    {"u": "DStach", "p": "Rydygiera*1"},
    {"u": "AK2150", "p": "Rydygiera*1"},
    {"u": "Iwo2150", "p": "Rydygiera*1"},
    {"u": "Magdacie", "p": "Rydygiera*1"},
    {"u": "WNeli", "p": "Rydygiera*1"},
    {"u": "MS2150", "p": "ZElki213*"}
    {"u": "NekroFILLLLLLLL", "p": "Pornosek123!"},
]

# BAZA PLU
RAW_PLU_DATA = {
    # Owoce
    "Ananas": 505, "Arbuz": 180, "Awokado zielone": 152, "Bio Awocado": 348,
    "Banany": 100, "Bio Banany Premium": 829, "Brzoskwinie": 220, "Brzoskwinie ciasteczkowe": 606,
    "Cytryny": 535, "Czereśnie": 92, "Granat": 208, "Grejpfrut czerwony": 116,
    "Gruszka Rocha": 8584, "Gruszki Abate": 3762, "Gruszki czerwone": 4410, "Gruszki deserowe": 5031,
    "Gruszki Klapsa": 5059, "Gruszki polskie": 3759, "Jabłka Gala": 8109, "Kaki szt.": 8351,
    "Kasztany jadalne": 6119, "Kiwi": 140, "Kiwi Gold": 5993, "Liczi": 159, "Limetka": 110,
    "Mandarynki": 568, "Mandarynki XXL": 5515, "Mango": 160, "Melon zielony": 7519,
    "Melon żółty": 186, "Morele": 789, "Nektarynki": 230, "Nektarynki ciasteczkowe": 6441,
    "Orzechy laskowe": 6152, "Pomarańcze XXL": 501, "Śliwki niebieskie": 820,
    "Śliwki okrągłe": 243, "Truskawki polskie": 4239, "Winogrono ciemne": 821,
    "Winogrono jasne": 250, "Winogrono różowe Red Globe": 255, "Żurawina": 8141,
    # Warzywa
    "Bakłażan": 426, "Bataty": 916, "Bio Dynia Hokkaido": 7808, "Brukselka": 375,
    "Buraki czerwone": 514, "Cebula bez łuski": 609, "Cebula czerwona": 242,
    "Cebula szalotka": 8518, "Cebula żółta": 3291, "Cukinia": 425, "Czosnek luz": 615,
    "Czosnek młody": 543, "Dynia Hokkaido": 428, "Dynia luz": 427, "Dynia malowana": 7422,
    "Dynia piżmowa": 6008, "Fasola szparagowa żółta": 773, "Groszek cukrowy, luz": 6625,
    "Imbir": 525, "Kalafior, szt.": 430, "Kapusta biała": 360, "Kapusta biała młoda, szt.": 361,
    "Kapusta czerwona": 365, "Kapusta gołąbkowa": 6071, "Kapusta pekińska młoda": 370,
    "Marchew": 322, "Ogórki gruntowe": 422, "Ogórki gruntowe polskie": 9065,
    "Ogórki zielone": 2233, "Ogórki zielone polskie": 1709, "Papryka czerwona": 380,
    "Papryka słodka": 896, "Papryka zielona": 126, "Papryka żółta": 385,
    "Papryczki pikantne": 6919, "Pietruszka": 558, "Pomidory Jedyne Malinowe": 8627,
    "Pomidory kiściowe": 410, "Pomidory malinowe karbowane": 1895, "Pomidory Marmande": 8586,
    "Pomidory rzymskie": 8165, "Pomidory truskawkowe": 93, "Sałata masłowa": 300,
    "Seler": 342, "Ziemniaki jadalne": 7239, "Ziemniaki jadalne myte": 497,
    # Pieczywo
    "Bagietka czosnkowa": 14, "Bagietka duża pszenna": 7490, "Bagietka w stylu francuskim": 8746,
    "Bajgiel z makiem": 2399, "Bochen orkiszowy na kam. z witamin.": 9442,
    "Bochen rustykalny na kamieniu": 4119, "Bułka bawarska": 836, "Bułka fitness": 9486,
    "Bułka grahamka": 7760, "Bułka kajzerka pszenna": 549, "Bułka kajzerka wieloziarnista": 9,
    "Bułka mleczna": 7563, "Bułka nacięta": 8531, "Bułka orkiszowa na kamieniu": 4132,
    "Bułka Paryska na kamieniu": 4793, "Bułka pszenna oprószona mąką": 6110,
    "Bułka w stylu rustykalnym": 6106, "Bułka wysokobiałkowa": 8830, "Bułka z dynią": 8778,  
    "Bułka z kiełkami żyta": 545, "Bułka z ziarnami psz.-żyt.": 833, "Bułka ze skyrem": 9951,
    "Bułka ziarnella": 7611, "Bułka ziemniaczana": 524, "Bułka ziemniaczana z ziarnami": 841,
    "Cebularz": 4827, "Chleb Baltonowski": 36, "Chleb drwalski": 34, "Chleb górski": 802,
    "Chleb na maślance": 856, "Chleb pełen ziaren": 2094, "Chleb słonecznikowy": 32,
    "Chleb typu włoskiego": 35, "Chleb wieloziarnisty na kamieniu": 9267,
    "Chleb wysokobiałkowy Oskroba": 9585, "Chleb z ziarnami owsa": 8822, "Chleb żytni": 872,
    "Ciabatta": 22, "Ciastko z jabłkiem": 7231, "Croissant malinowy": 9886,
    "Croissant maślany 27% masła": 565, "Croissant pistacjowy": 9430,
    "Croissant w stylu dubajskim": 9883, "Croissant z nadzieniem orzech.": 9778,
    "Donut czekoladowy": 8804, "Donut Milka": 474, "Donut Pinky": 6724,
    "Drożdżówka SORT. (wiśnia/śliwka/ser)": 8850, "Drożdżówka z budyniem": 817,
    "Drożdżówka z serem": 2700, "Fantazja truskawkowa": 47, "Frusta Prosciutto": 506,
    "Hot-Dog": 52, "Jagodzianka": 8687, "Mini-Calzone Margherita": 2719,
    "Pasztecik z pieczarkami": 48, "Pączek pistacjowy": 8385, "Pączek w stylu dubajskim": 9881,
    "Pinsa Margherita": 8238, "Pizzerina z szynką i pieczarkami": 9450,
    "Precel": 8, "Przekąska z czekoladą": 42, "Przekąska z serem": 7380,
    "Półbagietka": 95, "Rogal maślany": 814, "Zapiekanka z pieczarkami i serem": 7957,
    # Słodycze / Inne
    "Hellena Oranżada Galaretka": 4496, "Mieszko Michaszki": 2378, "Mieszko Trufle": 2377,
    "Mieszko Wiśnie w alkoholu": 1362, "Śliwka Nałęczowska Solidarność": 548,
    "Śliwka w czekoladzie Mister Choc": 5778, "Wawel Fresh&Fruity galaretki": 553,
    "Wawel Tiki Taki": 527, "Zozole MUSSS": 4772, "Zozole sorbet arbuzowy": 9990
}

plu_dict = {normalize_name(k): v for k, v in RAW_PLU_DATA.items()}

# ----------------------------------------------------
# 5. GŁÓWNA LOGIKA
# ----------------------------------------------------
print(f"🚀 [AUTO-PILOT] Rozpoczynam pracę na {len(ACCOUNTS)} kontach. Tryb: 2 testy per konto.")

for idx, current_acc in enumerate(ACCOUNTS):
    driver = None
    try:
        driver = get_driver()
        wait = WebDriverWait(driver, 10)
        
        print(f"\n[{idx+1}/{len(ACCOUNTS)}] 👤 {current_acc['u']}")
        
        # 1. LOGOWANIE
        driver.get(URL_LOGIN)
        email_el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, EMAIL_SELECTOR)))
        email_el.clear()
        email_el.send_keys(current_acc['u'])
        pass_el = driver.find_element(By.CSS_SELECTOR, PASS_SELECTOR)
        pass_el.clear()
        pass_el.send_keys(current_acc['p'])
        pass_el.send_keys(Keys.ENTER)
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, BTN_TEST_PLU)))
        time.sleep(1)

        # 2. PĘTLA TESTÓW (DOKŁADNIE 2 RAZY)
        for test_round in range(2):
            print(f"   ▶️ Rozpoczynam TEST {test_round + 1} z 2")

            # ZAWSZE startuj z Dashboardu - to jest pewniejsze niż przycisk "Spróbuj ponownie"
            if test_round > 0:
                driver.get(URL_LOGIN) # To nas przeniesie na dashboard
                time.sleep(2)

            try:
                # Kliknij test wiedzy
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, BTN_TEST_PLU))).click()
                # Kliknij "wszystkie artykuły"
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, BTN_ALL_ARTICLES))).click()
                # Kliknij ewentualny Step 2 (jeśli istnieje)
                try:
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, BTN_STEP_2_GROUP))).click()
                except: pass
            except Exception as e:
                print(f"      ⚠️ Błąd nawigacji do testu: {e}")
                continue

            # Pętla odpowiadania na pytania
            time.sleep(2)
            last_product_name = ""
            
            while True:
                # Sprawdź, czy test się zakończył (czy widać przycisk podsumowania)
                try:
                    end_btns = driver.find_elements(By.CSS_SELECTOR, BTN_TRY_AGAIN)
                    if end_btns and end_btns[0].is_displayed():
                        print(f"   🏁 Koniec testu {test_round + 1}.")
                        break 
                except: pass

                # Sprawdź nazwę produktu
                try:
                    name_el = driver.find_elements(By.XPATH, PRODUCT_NAME_XPATH)
                    if not name_el:
                        time.sleep(0.5)
                        continue
                    
                    current_name = name_el[0].text.strip()
                    
                    if not current_name or current_name == last_product_name or "koniec" in current_name.lower():
                        time.sleep(0.3)
                        continue

                    kod = plu_dict.get(normalize_name(current_name))
                    
                    if kod:
                        inp = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, PLU_INPUT)))
                        inp.clear()
                        inp.send_keys(str(kod))
                        inp.send_keys(Keys.ENTER)
                        last_product_name = current_name
                    else:
                        # print(f"      ⚠️ BRAK KODU: '{current_name}' -> 0000")
                        inp = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, PLU_INPUT)))
                        inp.clear()
                        inp.send_keys("0000")
                        inp.send_keys(Keys.ENTER)
                        last_product_name = current_name
                        time.sleep(0.5)
                        
                except Exception as e:
                    time.sleep(0.5)

        # 3. WYLOGOWANIE PO 2 TESTACH
        print("   🚪 Wylogowywanie...")
        try:
            logout_el = driver.find_element(By.CSS_SELECTOR, LOGOUT_BTN)
            driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {view: window, bubbles:true, cancelable: true}));", logout_el)
            time.sleep(2)
        except Exception as e:
            print(f"   ⚠️ Problem z wylogowaniem: {e}")

    except Exception as e:
        print(f"❌ Błąd krytyczny konta {current_acc['u']}: {e}")
    finally:
        if driver: driver.quit()
        time.sleep(1)

print("\n🎉 ZAKOŃCZONO WSZYSTKIE KONTA.")
