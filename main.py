import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)

    driver.get("https://orteil.dashnet.org/cookieclicker/")

    lang_select = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "langSelect-EN"))
    )
    lang_select.click()

    wait = WebDriverWait(driver, 60)
    big_cookie = wait.until(EC.presence_of_element_located((By.ID, "bigCookie")))

    buy_logic_script = """
    var choices = [];

    var baseCps = {
        "Cursor": 0.1, "Grandma": 1, "Farm": 8, "Mine": 47, "Factory": 260,
        "Bank": 1400, "Temple": 7800, "Wizard Tower": 44000, "Shipment": 260000,
        "Alchemy Lab": 1600000, "Portal": 10000000, "Time Machine": 65000000,
        "Antimatter Condenser": 430000000, "Prism": 2900000000, "Chancemaker": 21000000000,
        "Fractal Engine": 150000000000, "Javascript Console": 1100000000000,
        "Idleverse": 8300000000000, "Cortex Baker": 64000000000000, "You": 510000000000000
    };

    for (var i in Game.ObjectsById) {
        var obj = Game.ObjectsById[i];
        if (obj.locked) continue;

        var gain = (obj.amount > 0 && obj.storedCps > 0) ?
            obj.storedCps / obj.amount :
            (baseCps[obj.name] || 0.1);

        choices.push({
            type: "Building",
            obj: obj,
            price: obj.price,
            gain: gain,
            payback: obj.price / gain
        });
    }

    for (var i in Game.UpgradesById) {
        var up = Game.UpgradesById[i];
        if (up.locked && !up.isVaulted) continue;

        var price = up.getPrice();
        var gain = 0;

        if (up.buildingTie) {
            gain = up.buildingTie.storedCps || 0.0001;
        } else if (up.pool === "cookie") {
            gain = Game.cookiesPs * 0.1;
        } else {
            gain = Game.cookiesPs * 0.05;
        }

        choices.push({
            type: "Upgrade",
            obj: up,
            price: price,
            gain: gain,
            payback: price / gain
        });
    }

    choices.sort((a,b)=>a.payback-b.payback);
    if (choices.length === 0) return null;

    var best = choices[0];

    var clickCps = Game.computedMouseCps * 10;
    var effectiveCps = Game.cookiesPs + clickCps;
    if (effectiveCps <= 0) effectiveCps = 0.1;

    if (best.price <= Game.cookies) {
        best.obj.buy();
        return best.obj.name;
    }

    var waitTime = (best.price - Game.cookies) / effectiveCps;

    for (var i = 1; i < choices.length; i++) {
        var c = choices[i];
        if (c.price > Game.cookies) continue;

        var after = Game.cookies - c.price;
        var newCps = effectiveCps + c.gain;
        var newTime = (best.price - after) / newCps;

        if (newTime < waitTime) {
            c.obj.buy();
            return c.obj.name;
        }
    }

    return null;
    """

    while True:
        try:
            big_cookie.click()
        except Exception:
            try:
                big_cookie = driver.find_element(By.ID, "bigCookie")
                big_cookie.click()
            except Exception:
                pass

        driver.execute_script(buy_logic_script)

        time.sleep(0.01)

if __name__ == "__main__":
    main()
