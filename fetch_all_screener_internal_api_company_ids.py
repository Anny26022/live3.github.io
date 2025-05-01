import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re
import json


def get_peer_api_company_id(symbol, log_file=None):
    url = f"https://www.screener.in/company/{symbol}/"
    # Enable browser logging
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = webdriver.Chrome(options=chrome_options)
    logs_for_this_symbol = []
    def log(msg):
        print(msg)
        logs_for_this_symbol.append(msg)
    try:
        log(f"[START] {symbol}: Fetching {url}")
        driver.get(url)
        time.sleep(2)
        # Click the Peers tab
        try:
            peers_tab = driver.find_element(By.XPATH, "//a[contains(text(), 'Peers')]")
            peers_tab.click()
            log(f"[CLICK] Peers tab clicked for {symbol}")
            time.sleep(3)  # Wait for XHR to fire and load
        except Exception as e:
            log(f"[WARN] Could not click Peers tab for {symbol}: {e}")
        # Extract network logs, filter for XHR and peers
        logs = driver.get_log("performance")
        peer_api_found = False
        for entry in logs:
            msg = entry["message"]
            if '"Network.requestWillBeSent"' in msg and "/api/company/" in msg and "/peers/" in msg:
                try:
                    data = json.loads(msg)
                    request_url = data["message"]["params"]["request"]["url"]
                    m = re.search(r'/api/company/(\d+)/peers/', request_url)
                    if m:
                        company_id = m.group(1)
                        log(f"[OK] {symbol}: Peer API company ID = {company_id}")
                        peer_api_found = True
                        break
                except Exception as e:
                    log(f"[WARN] Could not parse log entry for {symbol}: {e}")
        if not peer_api_found:
            log(f"[FAIL] {symbol}: No API company ID found in XHR logs")
        # Log a summary of network log entries
        log(f"[LOGS] {symbol}: Total network log entries: {len(logs)}")
        for entry in logs[:5]:
            log(f"[LOGS] {symbol}: {entry['message'][:300]}")
    except Exception as e:
        log(f"[ERROR] {symbol}: {e}")
    finally:
        driver.quit()
        # Save logs for this symbol to file
        if log_file:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write('\n'.join(logs_for_this_symbol) + '\n')
    # Return company_id if found
    for line in logs_for_this_symbol:
        if line.startswith('[OK]'):
            return line.split('=')[1].strip()
    return None


def main():
    csv_path = "screener_all_listed_company_ids.csv"
    log_file = "screener_internal_api_id_log.txt"
    df = pd.read_csv(csv_path, dtype=str)
    symbols = df['Symbol'].astype(str).unique().tolist()

    # Clear log file at start
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write('')

    results = []
    for symbol in symbols:
        company_id_consolidated = get_peer_api_company_id(symbol + "/consolidated", log_file=log_file)
        time.sleep(0.1)
        results.append({
            "Symbol": symbol,
            "CompanyID_Consolidated": company_id_consolidated if company_id_consolidated else ''
        })

    # Save to CSV
    new_df = pd.DataFrame(results)
    new_df.drop_duplicates(subset=["Symbol"], inplace=True)
    new_df.to_csv("screener_all_listed_company_ids.csv", index=False)
    print(f"Done! Found {len(new_df)} companies. Saved to screener_all_listed_company_ids.csv.")
    print(f"Detailed logs for each company saved in {log_file}")

if __name__ == "__main__":
    main()
