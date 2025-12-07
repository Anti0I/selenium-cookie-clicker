from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# --- BAZOWE WARTOŚCI BUDYNKÓW (tylko te osiągalne w 8 min) ---
BASE_PRICES = {
    "Cursor": 15,
    "Grandma": 100,
    "Farm": 1100,
    "Mine": 12000,
    "Factory": 130000,
    "Bank": 1400000,
}

BASE_CPS = {
    "Cursor": 0.1,
    "Grandma": 1,
    "Farm": 8,
    "Mine": 47,
    "Factory": 260,
    "Bank": 1400,
}

PRICE_MULTIPLIER = 1.15
building_count = {}


def parse_number(text):
    """Parsuje tekst na liczbę (np. '1,234' -> 1234)"""
    text = text.lower().strip().replace(",", "")
    match = re.search(r"[\d.]+", text)
    return float(match.group()) if match else 0


def get_price(name):
    """Oblicza aktualną cenę budynku"""
    base = BASE_PRICES.get(name, 0)
    count = building_count.get(name, 0)
    return int(base * (PRICE_MULTIPLIER ** count))


def main():
    global building_count
    
    # --- KONFIGURACJA ---
    options = webdriver.ChromeOptions()
    options.add_argument("--mute-audio")
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)

    print("Łączenie z localhost:8000...")
    driver.get("http://localhost:8000")

    # Wybór języka
    try:
        lang = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "langSelect-EN"))
        )
        lang.click()
        print("Język wybrany.")
    except:
        print("Pominięto wybór języka.")

    # Znajdź ciastko
    print("Szukam ciastka...")
    big_cookie = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "bigCookie"))
    )
    print("START!")

    last_check = time.time()
    estimated_cps = 1.0
    
    def get_cookies():
        try:
            text = driver.find_element(By.ID, "cookies").text.split()[0]
            return parse_number(text)
        except:
            return 0

    while True:
        try:
            # 1. KLIKANIE
            for _ in range(20):
                big_cookie.click()
            
            # 2. Sprawdzaj co 0.5s
            now = time.time()
            if now - last_check < 0.5:
                continue
            last_check = now

            # 3. ZŁOTE CIASTKO - kliknij jeśli jest!
            golden = driver.find_elements(By.CSS_SELECTOR, ".shimmer")
            if golden:
                golden[0].click()
                print("🌟 Złote ciastko!")

            # 4. ULEPSZENIA - kup każde dostępne
            upgrades = driver.find_elements(By.CSS_SELECTOR, ".crate.upgrade.enabled")
            if upgrades:
                upgrades[0].click()
                print("⬆️ Kupiono ulepszenie!")

            # 5. BUDYNKI - wybierz najlepszy
            cookies = get_cookies()
            estimated_cps = 1.0
            for name, count in building_count.items():
                estimated_cps += BASE_CPS.get(name, 0) * count

            products = driver.find_elements(By.CSS_SELECTOR, ".product")
            if not products:
                continue

            candidates = []
            for p in products:
                try:
                    name = p.find_element(By.CSS_SELECTOR, ".title.productName").text.strip()
                    if name not in BASE_CPS:
                        continue
                    
                    can_afford = "enabled" in p.get_attribute("class")
                    price = get_price(name)
                    cps = BASE_CPS[name]
                    payback = price / cps
                    
                    save_time = 0 if cookies >= price else (price - cookies) / max(estimated_cps, 0.1)
                    total_time = save_time + payback
                    
                    candidates.append({
                        "el": p, "name": name, "price": price,
                        "payback": payback, "total": total_time, "afford": can_afford
                    })
                except:
                    continue

            if not candidates:
                continue

            candidates.sort(key=lambda x: x["total"])
            best = candidates[0]

            if best["afford"]:
                best["el"].click()
                building_count[best["name"]] = building_count.get(best["name"], 0) + 1
                print(f"✓ {best['name']} (payback: {best['payback']:.0f})")
            else:
                print(f"⏳ Czekam na: {best['name']} (brakuje: {best['price'] - cookies:.0f})")

        except KeyboardInterrupt:
            print("\nKoniec!")
            break
        except:
            continue


if __name__ == "__main__":
    main()