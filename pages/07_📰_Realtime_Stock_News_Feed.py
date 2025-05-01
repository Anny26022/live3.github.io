import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests
import time
import datetime
import re
import concurrent.futures
import pytz

st.set_page_config(page_title="Stock News", layout="centered", initial_sidebar_state="auto")
st.write('Streamlit version:', st.__version__)

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="auto_refresh")

st.markdown("""
# 📰 Real Time Stock News Feed


""")

NEWS_API_URL = "https://news-mediator.tradingview.com/news-flow/v2/news?filter=lang%3Aen_IN&filter=market%3Astock&filter=market_country%3AIN&client=screener&streaming=true"

STORY_API_URL = "https://news-headlines.tradingview.com/v3/story"

search_query = st.text_input("", "", placeholder="🔍 Symbol or keyword", key="news_search", label_visibility="collapsed")

# Custom CSS for compact search box
st.markdown("""
<style>
div[data-testid="stTextInput"] input {
    min-width: 110px;
    width: 100%;
    max-width: none;
    font-size: 0.98rem;
    padding: 0.29em 0.7em;
    border-radius: 7px;
    border: 1.4px solid #223e56;
    background: #223e56;
    color: #fff;
    margin-left: 0;
    margin-right: 0;
    display: block;
    box-shadow: 0 1px 8px 0 rgba(34,62,86,0.07);
}
</style>
""", unsafe_allow_html=True)


# Fetch news from TradingView API with caching
@st.cache_data(show_spinner=False)
def fetch_news():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://in.tradingview.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    resp = requests.get(NEWS_API_URL, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

# --- Fetch only new news based on latest timestamp ---
if 'latest_news_time' not in st.session_state:
    st.session_state['latest_news_time'] = None

refresh = st.button('🔄 Refresh News', key='refresh_news')

# Fetch news
news_data = fetch_news()

# --- Filter only new news ---
items = news_data.get('items', []) if news_data else []

# Find the latest timestamp in the current batch
latest_time = None
new_items = []
for item in items:
    published = item.get('published')
    # published is in ISO 8601 format, e.g., '2024-04-30T09:34:00Z'
    try:
        published_dt = datetime.datetime.strptime(published, '%Y-%m-%dT%H:%M:%SZ')
    except Exception:
        published_dt = None
    if published_dt:
        if (st.session_state['latest_news_time'] is None) or (published_dt > st.session_state['latest_news_time']):
            new_items.append(item)
        if (latest_time is None) or (published_dt > latest_time):
            latest_time = published_dt

# Update session state with the latest news timestamp
if latest_time:
    st.session_state['latest_news_time'] = latest_time

# Use new_items if not empty, else fallback to all items
if new_items:
    items = new_items

# --- END fetch only new news logic ---

# Existing code continues below as before

st.cache_data.clear()

data = fetch_news()
stories = data.get('items', [])

if stories:
    try:
        from usd_inr_exchange_rate import get_usd_inr_rate
        usd_inr = get_usd_inr_rate()
        def convert_usd_to_crore(match):
            # Skip if we're inside a crore conversion already
            if re.search(r'₹.*Crore.*\(.*\$.*Million\)', match.string[:match.start()]):
                return match.group(0)
            usd = float(match.group(1).replace(',', ''))
            inr = usd * usd_inr
            crores = inr / 1e7
            if crores == int(crores):
                crores_str = f"{int(crores)}"
            else:
                crores_str = f"{crores:.2f}".rstrip('0').rstrip('.')
            # Handle zero crore special case
            if float(crores) == 0:
                return "₹0 Crore"
            return f"₹{crores_str} Crore (${match.group(1)} Million)"

        def convert_rupees_to_crore(match):
            # Skip if we're inside a crore conversion already
            if re.search(r'₹.*Crore.*\(.*\$.*Million\)', match.string[:match.start()]):
                return match.group(0)
            rupees = float(match.group(1).replace(',', ''))
            crores = rupees / 1e7
            if crores == int(crores):
                crores_str = f"{int(crores)}"
            else:
                crores_str = f"{crores:.2f}".rstrip('0').rstrip('.')
            usd = rupees / usd_inr
            usd_millions = usd / 1e6
            # Handle zero crore special case
            if float(crores) == 0:
                return "₹0 Crore"
            if usd_millions >= 1:
                return f"₹{crores_str} Crore (${usd_millions:.2f}M)"
            return f"₹{crores_str} Crore"

        def convert_billion_rupees_to_crore(match):
            # Skip if we're inside a crore conversion already
            if re.search(r'₹.*Crore.*\(.*\$.*Million\)', match.string[:match.start()]):
                return match.group(0)
            billion_rupees = float(match.group(1).replace(',', ''))
            crores = billion_rupees * 100
            if crores == int(crores):
                crores_str = f"{int(crores)}"
            else:
                crores_str = f"{crores:.2f}".rstrip('0').rstrip('.')
            usd = (billion_rupees * 1e9) / usd_inr
            usd_millions = usd / 1e6
            # Handle zero crore special case
            if float(crores) == 0:
                return "₹0 Crore"
            if usd_millions >= 1:
                return f"₹{crores_str} Crore (${usd_millions:.2f}M)"
            return f"₹{crores_str} Crore"

        def convert_million_rupees_to_crore(match):
            # Skip if we're inside a crore conversion already
            if re.search(r'₹.*Crore.*\(.*\$.*Million\)', match.string[:match.start()]):
                return match.group(0)
            million_rupees = float(match.group(1).replace(',', ''))
            crores = million_rupees / 10
            if crores == int(crores):
                crores_str = f"{int(crores)}"
            else:
                crores_str = f"{crores:.2f}".rstrip('0').rstrip('.')
            usd = (million_rupees * 1e6) / usd_inr
            usd_millions = usd / 1e6
            # Handle zero crore special case
            if float(crores) == 0:
                return "₹0 Crore"
            if usd_millions >= 1:
                return f"₹{crores_str} Crore (${usd_millions:.2f}M)"
            return f"₹{crores_str} Crore"

        for item in stories:
            story_id = item.get('id', '')
            title = item.get('title', '')
            
            # Remove spurious ₹0 Crore from title if present (fix for hardcoded/erroneous value)
            if title:
                # Remove patterns like (₹0 Crore ...) or (Rs 0 Crore ...) or (INR 0 Crore ...)
                title = re.sub(r"\((?:₹|Rs|INR)\s*0\s*Crore[^)]*\)", "", title, flags=re.I)
                # Skip if already in the correct format (₹X Crore ($Y Million))
                if not re.search(r'₹\d+(?:\.\d+)?\s*Crore\s*\(\$\d+(?:\.\d+)?\s*Million\)', title, flags=re.I):
                    # Convert billion/million rupees to crores
                    title = re.sub(r"(\d+(?:\.\d+)?)\s*Billion Rupees?\b(?!\s*(?:Crore|Million))", convert_billion_rupees_to_crore, title, flags=re.I)
                    title = re.sub(r"(\d+(?:\.\d+)?)\s*Million Rupees?\b(?!\s*(?:Crore|Million))", convert_million_rupees_to_crore, title, flags=re.I)
                    
                    # Convert plain rupees to crores (only if not already in millions/billions)
                    if not re.search(r'(Million|Billion)\s*Rupees?', title, flags=re.I):
                        title = re.sub(r"(\d+(?:\.\d+)?)\s*Rupees?\b(?!\s*(?:Crore|Million))", convert_rupees_to_crore, title, flags=re.I)
                    
                    # Convert USD to crores
                    title = re.sub(r"\$\s*(\d+(?:\.\d+)?(?:,\d{3})*)\s*(?:Million|M)\b(?!\s*(?:Crore|Million))", convert_usd_to_crore, title, flags=re.I)
                    title = re.sub(r"(\d+(?:\.\d+)?)\s*Million Dollars?\b(?!\s*(?:Crore|Million))", convert_usd_to_crore, title, flags=re.I)
                    
                    # Handle variations of billion
                    title = re.sub(r"(\d+(?:\.\d+)?)\s*Bln Rupees?\b(?!\s*(?:Crore|Million))", convert_billion_rupees_to_crore, title, flags=re.I)
                    title = re.sub(r"(\d+(?:\.\d+)?)\s*B Rupees?\b(?!\s*(?:Crore|Million))", convert_billion_rupees_to_crore, title, flags=re.I)
                    
                    # Handle variations of million
                    title = re.sub(r"(\d+(?:\.\d+)?)\s*Mln Rupees?\b(?!\s*(?:Crore|Million))", convert_million_rupees_to_crore, title, flags=re.I)
                    title = re.sub(r"(\d+(?:\.\d+)?)\s*M Rupees?\b(?!\s*(?:Crore|Million))", convert_million_rupees_to_crore, title, flags=re.I)

            source = item.get('source', {}).get('display_name', '') if 'source' in item else ''
            ts = item.get('published', '')
            
            # Filter by search query (title/headline or related symbol, partial/case-insensitive)
            if search_query:
                query = search_query.lower().strip()
                symbol_match = False
                if 'relatedSymbols' in item and item['relatedSymbols']:
                    for s in item['relatedSymbols']:
                        symbol_val = str(s.get('symbol','')).lower()
                        if query in symbol_val:
                            symbol_match = True
                            break
                if not ((title and query in title.lower()) or symbol_match):
                    continue
            if story_id and title:
                # Beautiful card layout for news item
                card_html = """
                <div style="
                  background: #fff;
                  border-radius: 12px;
                  box-shadow: 0 1px 8px 0 rgba(60,72,90,0.06);
                  border: 1px solid #f0f0f0;
                  margin-bottom: 1.2rem;
                  padding: 1.1rem 1.3rem 1.1rem 1.3rem;
                  display: flex;
                  align-items: flex-start;
                  gap: 1.0rem;
                  transition: box-shadow 0.18s;
                ">
                  <div style="flex: 1;">
                    <div style="font-size:1.07rem;font-weight:600;color:#222;line-height:1.5;margin-bottom:0.28rem;">{title}</div>
                    {story_link}
                    <div style="margin: 0.3rem 0 0.15rem 0;">
                      <span style='color:#888;font-size:0.92rem;'>Published: {published}</span>
                      {urgency}
                    </div>
                    {badges}
                  </div>
                  <div style="text-align:center;min-width:70px;">
                    {provider_logo}

                  </div>
                </div>
                """
                # Prepare fields
                story_link = ""
                if 'storyPath' in item and item['storyPath']:
                    link = f"https://in.tradingview.com{item['storyPath']}"
                    story_link = f"<a href='{link}' target='_blank' style='color:#6EC1E4;font-weight:600;text-decoration:none;'>Read full story &#8599;</a>"
                published = ""
                if 'published' in item:
                    # Convert GMT/UTC timestamp to IST and format as 12-hour time
                    utc_dt = datetime.datetime.fromtimestamp(item['published'], tz=datetime.timezone.utc)
                    ist = pytz.timezone('Asia/Kolkata')
                    ist_dt = utc_dt.astimezone(ist)
                    published = ist_dt.strftime('%d-%m-%Y %I:%M %p IST')
                urgency = ""
                if 'urgency' in item and item['urgency']:
                    urgency = f"<span style='color:#FF6B6B;font-size:0.98rem;margin-left:1rem;'>Urgency: {item['urgency']}</span>"
                badges = ""
                import urllib.parse
                if 'relatedSymbols' in item and item['relatedSymbols']:
                    badges = '<div style="margin-top:0.6rem; display: flex; flex-wrap: wrap; gap: 8px 8px;">' + ''.join([
                        f"<a href='https://in.tradingview.com/chart/?symbol={urllib.parse.quote(s.get('symbol',''))}&interval=D' target='_blank' rel='noopener'><span style='background:#3498db;color:#fff;border-radius:6px;padding:4px 12px;font-size:0.93rem;font-weight:500;display:inline-block;margin-bottom:4px;cursor:pointer;text-decoration:none;'>{s.get('symbol','')}</span></a>"
                        for s in item['relatedSymbols']]) + '</div>'
                provider_logo = ""
                provider_name = ""
                if 'provider' in item and item['provider']:
                    prov = item['provider']
                    provider_name = prov.get('name','')
                    provider_id = prov.get('id','').lower() if 'id' in prov else ''
                    # Use special logo for known providers
                    logo_map = {
                        'reuters': 'https://s3.tradingview.com/news/logo/reuters--theme-light.svg',
                        'market-watch': 'https://s3.tradingview.com/news/logo/market-watch--theme-light.svg',
                        'dow-jones': 'https://s3.tradingview.com/news/logo/dow-jones--theme-light.svg',
                        'trading-economics': 'https://s3.tradingview.com/news/logo/trading-economics--theme-light.svg',
                        'forexlive': 'https://s3.tradingview.com/news/logo/forexlive--theme-light.svg',
                        'globenewswire': 'https://s3.tradingview.com/news/logo/globenewswire--theme-light.svg',
                        'gurufocus': 'https://s3.tradingview.com/news/logo/gurufocus--theme-light.svg',
                        'hse': 'https://s3.tradingview.com/news/logo/hse--theme-light.svg',
                        'ice': 'https://s3.tradingview.com/news/logo/ice--theme-light.svg',
                        'moneycontrol': 'https://s3.tradingview.com/news/logo/moneycontrol--theme-light.svg',
                        'mt-newswires': 'https://s3.tradingview.com/news/logo/mtnewswires--theme-light.svg',
                        'tradingview': 'https://s3.tradingview.com/news/logo/tradingview--theme-light.svg',
                        'marketbeat': 'https://s3.tradingview.com/news/logo/marketbeat--theme-light.svg',
                        'barchart': 'https://s3.tradingview.com/news/logo/barchart--theme-light.svg',
                        'cointelegraph': 'https://s3.tradingview.com/news/logo/cointelegraph--theme-light.svg',
                        'beincrypto': 'https://s3.tradingview.com/news/logo/beincrypto--theme-light.svg',
                        'zacks': 'https://s3.tradingview.com/news/logo/zacks--theme-light.svg',
                        'marketindex': 'https://s3.tradingview.com/news/logo/marketindex--theme-light.svg',
                        '11thestate': 'https://s3.tradingview.com/news/logo/11thestate--theme-light.svg',
                        'acceswire': 'https://s3.tradingview.com/news/logo/rdp-accesswire--theme-light.svg',
                        'acn': 'https://s3.tradingview.com/news/logo/acn--theme-light.svg',
                        'coindar': 'https://s3.tradingview.com/news/logo/coindar--theme-light.svg',
                        'coinmarketcal': 'https://s3.tradingview.com/news/logo/coinmarketcal--theme-light.svg',
                        'congressional_quarterly': 'https://s3.tradingview.com/news/logo/congressional_quarterly--theme-light.svg',
                        'cse': 'https://s3.tradingview.com/news/logo/cse--theme-light.svg',
                        'cryptobriefing': 'https://s3.tradingview.com/news/logo/cryptobriefing--theme-light.svg',
                        'cryptoglobe': 'https://s3.tradingview.com/news/logo/cryptoglobe--theme-light.svg',
                        'cryptonews': 'https://s3.tradingview.com/news/logo/cryptonews--theme-light.svg',
                        'cryptopotato': 'https://s3.tradingview.com/news/logo/cryptopotato--theme-light.svg',
                        'dailyfx': 'https://s3.tradingview.com/news/logo/dailyfx--theme-light.svg',
                        'etfcom': 'https://s3.tradingview.com/news/logo/etfcom--theme-light.svg',
                        'financemagnates': 'https://s3.tradingview.com/news/logo/financemagnates--theme-light.svg',
                        'financial_juice': 'https://s3.tradingview.com/news/logo/financial_juice--theme-light.svg',
                        'forexlive': 'https://s3.tradingview.com/news/logo/forexlive--theme-light.svg',
                        'globenewswire': 'https://s3.tradingview.com/news/logo/rdp-gnw--theme-light.svg',
                        'gurufocus': 'https://s3.tradingview.com/news/logo/gurufocus--theme-light.svg',
                        'hse': 'https://s3.tradingview.com/news/logo/hse--theme-light.svg',
                        'ice': 'https://s3.tradingview.com/news/logo/ice--theme-light.svg',
                        'investorplace': 'https://s3.tradingview.com/news/logo/investorplace--theme-light.svg',
                        'invezz': 'https://s3.tradingview.com/news/logo/invezz--theme-light.svg',
                        'jcn': 'https://s3.tradingview.com/news/logo/jcn--theme-light.svg',
                        'leverage_shares': 'https://s3.tradingview.com/news/logo/leverage_shares--theme-light.svg',
                        'lse': 'https://s3.tradingview.com/news/logo/rdp-lse--theme-light.svg',
                        'macenews': 'https://s3.tradingview.com/news/logo/macenews--theme-light.svg',
                        'miranda_partners': 'https://s3.tradingview.com/news/logo/miranda_partners--theme-light.svg',
                        'modular_finance': 'https://s3.tradingview.com/news/logo/modular_finance--theme-light.svg',
                        'nbd': 'https://s3.tradingview.com/news/logo/nbd--theme-light.svg',
                        'newsbtc': 'https://s3.tradingview.com/news/logo/newsbtc--theme-light.svg',
                        'newsfilecorp': 'https://s3.tradingview.com/news/logo/newsfilecorp--theme-light.svg',
                        'obi': 'https://s3.tradingview.com/news/logo/obi--theme-light.svg',
                        'polish_emitent': 'https://s3.tradingview.com/news/logo/polish_emitent--theme-light.svg',
                        'polymerupdate': 'https://s3.tradingview.com/news/logo/polymerupdate--theme-light.svg',
                        'pressetext': 'https://s3.tradingview.com/news/logo/pressetext--theme-light.svg',
                        'rse': 'https://s3.tradingview.com/news/logo/rse--theme-light.svg',
                        'see_news': 'https://s3.tradingview.com/news/logo/see_news--theme-light.svg',
                        'smallcaps': 'https://s3.tradingview.com/news/logo/smallcaps--theme-light.svg',
                        'stocknews': 'https://s3.tradingview.com/news/logo/stocknews--theme-light.svg',
                        'tlse': 'https://s3.tradingview.com/news/logo/tlse--theme-light.svg',
                        'the_block': 'https://s3.tradingview.com/news/logo/the_block--theme-light.svg',
                        'thenewswire': 'https://s3.tradingview.com/news/logo/thenewswire--theme-light.svg',
                        'todayq': 'https://s3.tradingview.com/news/logo/todayq--theme-light.svg',
                        'u_today': 'https://s3.tradingview.com/news/logo/u_today--theme-light.svg',
                        'valuewalk': 'https://s3.tradingview.com/news/logo/valuewalk--theme-light.svg',
                        'zawya': 'https://s3.tradingview.com/news/logo/zawya--theme-light.svg',
                        'zycrypto': 'https://s3.tradingview.com/news/logo/zycrypto--theme-light.svg',
                        'london-stock-exchange': 'https://s3.tradingview.com/news/logo/rdp-lse--theme-light.svg',
                        'rdp-lse': 'https://s3.tradingview.com/news/logo/rdp-lse--theme-light.svg',
                        'rdp-gnw': 'https://s3.tradingview.com/news/logo/rdp-gnw--theme-light.svg',
                        'rdp-accesswire': 'https://s3.tradingview.com/news/logo/rdp-accesswire--theme-light.svg',
                        'accesswire': 'https://s3.tradingview.com/news/logo/rdp-accesswire--theme-light.svg',
                        'access-wire': 'https://s3.tradingview.com/news/logo/rdp-accesswire--theme-light.svg'
                    }
                    if provider_id in logo_map:
                        provider_logo = f"<img src='{logo_map[provider_id]}' style='max-width:80px;max-height:54px;width:auto;height:auto;display:block;margin:0 auto 8px auto;background:#fff;padding:3px;border-radius:10px;' alt='{provider_name} logo'/>"
                        print(f"Provider details - ID: {provider_id}, Name: {provider_name}, Full provider data: {prov}")
                    else:
                        # Try case-insensitive match
                        provider_id_lower = provider_id.lower() if provider_id else ''
                        logo_map_lower = {k.lower(): v for k, v in logo_map.items()}
                        if provider_id_lower in logo_map_lower:
                            provider_logo = f"<img src='{logo_map_lower[provider_id_lower]}' style='max-width:80px;max-height:54px;width:auto;height:auto;display:block;margin:0 auto 8px auto;background:#fff;padding:3px;border-radius:10px;' alt='{provider_name} logo'/>"
                            print(f"Found provider with case-insensitive match - Original ID: {provider_id}, Matched ID: {provider_id_lower}")
                        else:
                            logo_id = prov.get('logo_id')
                            print(f"Provider not found in logo_map - ID: {provider_id}, Name: {provider_name}, Full provider data: {prov}")
                            if logo_id:
                                # Use an <img> tag with onerror fallback to initials
                                initials = provider_name[:2].upper() if provider_name else "?"
                                provider_logo = f"<img src='https://s3-symbol-logo.tradingview.com/{logo_id}.svg' style='width:60px;height:60px;border-radius:50%;background:#fff;padding:3px 3px;' alt='{provider_name} logo' onerror=\"this.onerror=null;this.style.display='none';document.getElementById('prov_{story_id}').style.display='flex';\">"
                                provider_logo += f"<div id='prov_{story_id}' style='display:none;justify-content:center;align-items:center;width:60px;height:60px;border-radius:50%;background:#6EC1E4;color:#fff;font-size:1.6rem;font-weight:bold;'>{initials}</div>"
                            else:
                                initials = provider_name[:2].upper() if provider_name else "?"
                                provider_logo = f"<div style='display:flex;justify-content:center;align-items:center;width:48px;height:48px;border-radius:50%;background:#6EC1E4;color:#fff;font-size:1.4rem;font-weight:bold;'>{initials}</div>"
                st.markdown(card_html.format(
                    title=title,
                    story_link=story_link,
                    published=published,
                    urgency=urgency,
                    badges=badges,
                    provider_logo=provider_logo,
                    provider_name=provider_name
                ), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Failed to fetch news: {e}")
else:
    st.warning("No news headlines found in the 'items' array. .")