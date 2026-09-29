"""MoneyMindz: reply to /wallstreet in the Telegram group via GitHub Actions."""

import json
import os
import urllib.parse
import urllib.error
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
BOT_API = f'https://api.telegram.org/bot{TOKEN}/'
SYMBOLS = (
    ('S&P 500', '%5EGSPC'),
    ('Nasdaq', '%5EIXIC'),  # Nasdaq Composite, geen Nasdaq 100 of futures
    ('Dow Jones', '%5EDJI'),
)


class TelegramApiError(Exception):
    def __init__(self, code, description):
        self.code = code
        super().__init__(f'Telegram HTTP {code}: {description}')


def request_json(url, fields=None):
    body = json.dumps(fields).encode() if fields is not None else None
    headers = {'User-Agent': 'Mozilla/5.0 (MoneyMindzWallStreet/1.0)'}
    if body is not None:
        headers['Content-Type'] = 'application/json'
    request = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def telegram(method, **fields):
    try:
        result = request_json(BOT_API + method, fields)
    except urllib.error.HTTPError as exc:
        try:
            description = json.load(exc).get('description', 'Geen beschrijving')
        except (ValueError, OSError):
            description = 'Geen beschrijving'
        raise TelegramApiError(exc.code, description) from None
    if not result.get('ok'):
        raise TelegramApiError(result.get('error_code', 0),
                               result.get('description', 'Telegram-fout'))
    return result['result']


def quote(name, symbol):
    data = request_json(
        f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
        '?interval=1m&range=1d'
    )
    result = (data.get('chart') or {}).get('result') or []
    meta = result[0].get('meta') if result else None
    price = meta.get('regularMarketPrice') if meta else None
    previous = (meta.get('previousClose') or meta.get('chartPreviousClose')) if meta else None
    stamp = meta.get('regularMarketTime') if meta else None
    if (not isinstance(price, (int, float)) or price <= 0 or
            not isinstance(previous, (int, float)) or previous <= 0 or
            not isinstance(stamp, int)):
        raise ValueError(f'Geen geldige koers voor {name}')
    return price, previous


def nl_points(value):
    return f'{value:,.0f}'.replace(',', '.')


def nl_percent(value):
    return f'{value:+.2f}'.replace('.', ',') + '%'


def answer():
    now = datetime.now(ZoneInfo('Europe/Amsterdam'))
    sections = []
    for name, symbol in SYMBOLS:
        price, previous = quote(name, symbol)
        change = (price / previous - 1) * 100
        heading = 'S&P500' if name == 'S&P 500' else 'NASDAQ' if name == 'Nasdaq' else 'DOW JONES'
        sections.append(f'{heading}\n{nl_points(price)} pt\n{nl_percent(change)}')
    return f'{now:%d/%m/%Y %H:%M}\n\n' + '\n\n'.join(sections)


def is_command(text, username):
    first = text.strip().split(maxsplit=1)[0].lower() if text.strip() else ''
    return first in ('/wallstreet', f'/wallstreet@{username.lower()}')


def main():
    username = telegram('getMe')['username']
    updates = telegram('getUpdates', timeout=0, limit=100, allowed_updates=['message'])
    for update in updates:
        message = update.get('message') or {}
        chat = message.get('chat') or {}
        if chat.get('type') in ('group', 'supergroup') and is_command(message.get('text') or '', username):
            try:
                text = answer()
            except Exception as exc:
                print(f'Koersbron niet beschikbaar: {exc}')
                text = 'Koersen tijdelijk niet beschikbaar. Probeer het straks opnieuw.'
            try:
                telegram('sendMessage', chat_id=chat['id'], text=text,
                         reply_parameters={'message_id': message['message_id']})
                print(f'/wallstreet beantwoord in groep {chat["id"]}')
            except TelegramApiError as exc:
                if exc.code != 403:
                    raise
                # Deze groep weigert een bericht van de bot. Niet opnieuw blijven
                # proberen bij iedere geplande run; andere groepen blijven werken.
                print(f'Bericht overgeslagen in groep {chat["id"]}: {exc}')
        # Bevestig elk verwerkt update-ID; de volgende run reageert niet dubbel.
        telegram('getUpdates', offset=update['update_id'] + 1, limit=1,
                 timeout=0, allowed_updates=['message'])
    if not updates:
        print('Geen nieuwe berichten.')


if __name__ == '__main__':
    main()
