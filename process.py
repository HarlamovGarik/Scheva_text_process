from google_play_scraper import app, search
import re
import pandas as pd

def get_app_id(app_name_or_url):
    # Якщо це URL, витягуємо app ID
    match = re.search(r'id=([\w\.]+)', app_name_or_url)
    if match:
        return match.group(1)
    else:
        # Використовуємо пошук для знаходження застосунку за назвою
        results = search(app_name_or_url, lang='en', country='us', n=1)
        if results:
            return results[0]['appId']
        else:
            print("Застосунок не знайдено.")
            return None

def get_price_info(app_id, regions):
    price_info = []
    for region in regions:
        try:
            result = app(
                app_id,
                lang='en',
                country=region
            )
            region_code = region.upper()
            currency = result.get('currency', 'N/A')
            price = result.get('price', 'N/A')
            inAppProductPrice = result.get('inAppProductPrice', 'N/A')
            price_info.append({
                'Region Code': region_code,
                'Currency': currency,
                'in App Product Price': inAppProductPrice,
                'Current Price': price
            })
        except Exception as e:
            print(f"Помилка при отриманні даних для регіону {region}: {e}")
    return price_info

def main():
    app_name_or_url = input("Введіть назву застосунку або URL з Google Play Store: ")
    app_id = get_app_id(app_name_or_url)
    if app_id:
        regions = [
            'AR', 'AU', 'AT', 'BH', 'BY', 'BE', 'BO', 'BR', 'CA', 'CL', 'CO', 'CR', 'CZ', 'DK', 'DO', 'EC', 'EG', 'SV',
            'EE', 'FI', 'FR', 'DE', 'GR', 'GT', 'HN', 'HK', 'HU', 'IN', 'ID', 'IE', 'IT', 'JP', 'JO', 'KZ', 'KW', 'KG',
            'LV', 'LB', 'LT', 'LU', 'MY', 'MX', 'NL', 'NZ', 'NI', 'NO', 'OM', 'PA', 'PY', 'PE', 'PH', 'PL', 'PT', 'QA',
            'RO', 'RU', 'SA', 'SG', 'SK', 'ZA', 'KR', 'ES', 'SE', 'CH', 'TW', 'TH', 'TR', 'UA', 'AE', 'GB', 'US', 'UY',
            'UZ', 'VE', 'VN'
        ]
        price_info = get_price_info(app_id, regions)
        df = pd.DataFrame(price_info)
        print(f"Інформація про ціну для app ID: {app_id}")
        print(df)

if __name__ == "__main__":
    main()

