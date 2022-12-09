import re
from datetime import datetime

from .types import carTypes, cargoTypes

def my_round(val):
    if isinstance(val, float):
        if val % 1 > 0:
            return val
        elif val == 0.0:
            return '-'
        return int(val)

NOTIFY_TEMPLATE = """
<b>📅 {firstDate}</b>
<b>🔀 Маршрут:</b> {distanceTooltip}
<b>💰 Оплата:</b>
⤷ {price}
<b>🚚 Авто:</b>
{carTypes}
<b>📦 Груз:</b>
{loadingCargos}
<b>Рейтинг:</b> {rating}
<b>📞 Контакты:</b>
{contacts}
<b>🗒 Заметка:</b>
<i>{note}</i>
"""

CONTACT_TEMPLATE = """Имя: {name}
{phones}"""

NO_DATA = ""


def format_notify(data: dict) -> str:
    uv = {}
    uv['loading'] = data.get('loading', {})
    uv['date'] = datetime.fromisoformat(uv['loading'].get('firstDate', NO_DATA))
    uv['distancetooltip'] = data.get('route').get('distanceTooltip')
    loadings = uv['loading'].get('loadingCargos', {})
    uv['cargos'] = [cargoTypes[f"{cargo_type['nameId']}"].Name for cargo_type in loadings]
    load = data.get('load', {})
    uv['load'] = {k: my_round(v) for k, v in load.items()}
    uv['weight'] = uv['load'].get('weight', 0)
    uv['volume'] = uv['load'].get('volume', 0)
    uv['length'] = uv['load'].get('length', 0)
    uv['height'] = uv['load'].get('height', 0)
    uv['width'] = uv['load'].get('width', 0)
    uv['cargo_params'] = f"{uv['weight']} т / {uv['volume']} м"+ f", Д: {uv['length']}" if uv['length']!='-' else '' + f", Ш: {uv['width']}" if uv['width']!='-' else '' + f"" + f", В: {uv['height']}" if uv['height']!='-' else '' + f""
    uv['truck'] = data.get('truck', {})
    uv['car_types'] = [carTypes[car_type].Name for car_type in uv['truck']['carTypes']]
    uv['rate'] = data.get('rate', {})
    uv['firm'] = data.get('firm', {})
    uv['note'] = data.get('note', '')
    rating = uv['firm'].get('rating', NO_DATA)
    uv['description'] = rating.get('description', NO_DATA)
    uv['cash'] = uv['rate'].get('price', 0)
    uv['nds'] = int(uv['rate'].get('priceNds', 0))
    uv['nonds'] = int(uv['rate'].get('priceNoNds', 0))
    if uv['cash']+uv['nds']+uv['nonds']==0:
        uv['total_rate'] = 'Запрос ставки'
    else:
        uv['total_rate'] = f'С НДС: {uv["nds"]}' if uv["nds"]!=0 else '', f', БЕЗ НДС: {uv["nonds"]}' if uv["nonds"]!=0 else '', f', НАЛИЧКА: {uv["cash"]}' if uv["cash"]!=0 else ''
    uv['contacts'] = uv['firm'].get('contacts', {})
    uv['contacts_list'] = []
    for cont in uv['contacts']:
        uv['name'] = cont.get('name', NO_DATA)
        uv['phones'] = cont.get("phones", {})
        uv['phones_list'] = [ph.get("number") for ph in uv['phones']] if uv['phones'] else NO_DATA
        uv['phones_list'] = ['⤷ +' + re.sub(r'\D', r'', f'{ph}') for ph in uv['phones']] if uv['phones_list'] else NO_DATA
        uv['contact_fmt'] = CONTACT_TEMPLATE.format(
            name=uv['name'],
            phones="\n".join(uv['phones_list'])
        )
        uv['contacts_list'].append(uv['contact_fmt'])

    output_data = {  # return last load
        'firstDate': uv['date'].strftime("%d.%m.%Y"),
        'distanceTooltip': uv['distancetooltip'],
        'carTypes': ', '.join(uv['car_types']) if uv['truck'] else NO_DATA,
        'price': ''.join(uv['total_rate']),
        'rating': f'{uv["description"]}' if f"{uv['description']}" else NO_DATA,
        'contacts': "\n".join(uv['contacts_list']) if uv['contacts_list'] else NO_DATA,
        'note': uv['note'],
        'loadingCargos': ''.join(uv['cargos']) + ', ' + uv['cargo_params']
    }
    return NOTIFY_TEMPLATE.format(**output_data)

# class LogFormatter(logging.Formatter):
#     grey = "\x1b[38;20m"
#     yellow = "\x1b[33;20m"
#     red = "\x1b[31;20m"
#     bold_red = "\x1b[31;1m"
#     reset = "\x1b[0m"
#     format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
#
#     FORMATS = {
#         logging.DEBUG: grey + format + reset,
#         logging.INFO: grey + format + reset,
#         logging.WARNING: yellow + format + reset,
#         logging.ERROR: red + format + reset,
#         logging.CRITICAL: bold_red + format + reset
#     }
#
#     def format(self, record):
#         log_fmt = self.FORMATS.get(record.levelno)
#         formatter = logging.Formatter(log_fmt)
#         return formatter.format(record)