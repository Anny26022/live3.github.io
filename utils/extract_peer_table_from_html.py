import pandas as pd

def extract_peer_table_from_html(soup):
    """
    Extracts only the peer company rows (with data-row-company-id) from the peer comparison table.
    Returns a DataFrame with company names as clickable links. Ignores median/summary and unrelated tables.
    Args:
        soup (BeautifulSoup): Parsed HTML content.
    Returns:
        pd.DataFrame: DataFrame containing the peer companies, or None if not found.
    """
    tables = soup.find_all('table', class_='data-table')
    for table in tables:
        th_texts = [th.get_text(strip=True) for th in table.find_all('th')]
        if 'S.No.' in th_texts and 'Name' in th_texts:
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            rows = []
            for tr in table.find_all('tr', attrs={'data-row-company-id': True}):
                tds = tr.find_all('td')
                if len(tds) >= len(headers):
                    row = []
                    for i, td in enumerate(tds):
                        if headers[i] == "Name":
                            a = td.find('a')
                            if a:
                                name = a.get_text(strip=True)
                                href = a['href']
                                value = f"[{name}](https://www.screener.in{href})"
                            else:
                                value = td.get_text(strip=True)
                            row.append(value)
                        else:
                            row.append(td.get_text(strip=True))
                    rows.append(row)
            if rows:
                import pandas as pd
                df = pd.DataFrame(rows, columns=headers)
                return df
    return None
