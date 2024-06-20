from django.shortcuts import render
from .forms import UploadFileForm
import xml.etree.ElementTree as ET

def handle_uploaded_file(f):
    with open(f"uploads/{f.name}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    with open(f"uploads/{f.name}", "r", encoding="utf-8") as xml_file:
        with open(f"uploads/{f.name.replace('.xml', '.txt')}", "w") as txt_file:
            for line in xml_file:
                if "<date>" in line:
                    date_start = line.find("<date>")
                    date_end = line.find("</date>")
                    date_value = line[date_start + 6:date_end]
                    txt_file.write(f"Дата: {date_value}\n")

                if "<firmName>" in line:
                    firm_name_start = line.find("<firmName>")
                    firm_name_end = line.find("</firmName>")
                    firm_name_value = line[firm_name_start + 10:firm_name_end]
                    txt_file.write(f"Назва магазину: {firm_name_value}\n")

                if "<rate>" in line:
                    rate_start = line.find("<rate>")
                    rate_end = line.find("</rate>")
                    rate_value = line[rate_start + 6:rate_end]
                    txt_file.write(f"Курс доллару: {rate_value}\n")

                if "<delivery" in line:
                    delivery_info = parse_delivery_info(line)
                    if delivery_info:
                        txt_file.write(f"\n**Спосіб доставки ({delivery_info['type']})**\n")
                        txt_file.write(f"Кур'єрська служба: {delivery_info['carrier']}\n")
                        txt_file.write(f"Вартість доставки: {delivery_info['cost']}\n")

                if "<shipping" in line:
                    shipping_info = parse_shipping_info(line)
                    if shipping_info:
                        txt_file.write("\n**Відправка товару:**\n")
                        txt_file.write(f"По буднях: {shipping_info['workdays']}\n")
                        txt_file.write(f"У суботу: {shipping_info['saturday']}\n")
                        txt_file.write(f"У неділю: {shipping_info['sunday']}\n")

                if "<store" in line:
                    store_info = parse_store_info(line)
                    if store_info:
                        txt_file.write("\n**Пункт самовивезення:**\n")
                        txt_file.write(f"Назва: {store_info['name']}\n")
                        txt_file.write(f"Місто: {store_info['address']}\n")
                        txt_file.write(f"Час роботи:\n")
                        txt_file.write(f"    По буднях: {store_info['workdays_from']} - {store_info['workdays_to']}\n")
                        txt_file.write(f"    У суботу: {store_info['sat_from']} - {store_info['sat_to']}\n")
                        txt_file.write(f"    У неділю: {store_info['sun_from']} - {store_info['sun_to']}\n")

                if "<item>" in line:
                    item_info = parse_item_info(line)
                    if item_info:
                        txt_file.write("\n**Товар:**\n")
                        txt_file.write(f"Назва: {item_info['name']}\n")
                        txt_file.write(f"Бренд: {item_info['vendor']}\n")
                        txt_file.write(f"Опис: {item_info['description']}\n")
                        txt_file.write(f"Посилання: {item_info['url']}\n")
                        txt_file.write(f"Зображення: {item_info['image']}\n")
                        txt_file.write(f"Ціна: {item_info['priceRUAH']}\n")
                        txt_file.write(f"Наявність: {item_info['stock']}\n")
                        txt_file.write(f"Гарантія: {item_info['guarantee']}\n")
                        txt_file.write(f"Країна виготовлення: {item_info['param'][0]['value']}\n")
                        txt_file.write(f"Оригінальність: {item_info['param'][1]['value']}\n")

def parse_delivery_info(line):
    delivery_info = {}
    attributes = line.split(' ')

    for attribute in attributes:
        if '=' in attribute:
            key, value = attribute.split('=')
            value = value.replace('"', '').replace("'", "")
            delivery_info[key] = value

    if 'type' not in delivery_info or 'carrier' not in delivery_info or 'cost' not in delivery_info:
        return None

    return delivery_info


def parse_shipping_info(line):
    shipping_info = {}
    attributes = line.split(' ')

    for attribute in attributes:
        if '=' in attribute:
            key, value = attribute.split('=')
            value = value.replace('"', '').replace("'", "")
            shipping_info[key] = value

    if 'workdays' not in shipping_info or 'saturday' not in shipping_info or 'sunday' not in shipping_info:
        return None

    shipping_info['saturday'] = shipping_info['saturday'][:-14]

    return shipping_info

def parse_store_info(line):
    store_info = {}
    attributes = line.split(' ')

    for attribute in attributes:
        if '=' in attribute:
            key, value = attribute.split('=')
            value = value.replace('"', '').replace("'", "")
            store_info[key] = value

    if 'id' not in store_info or 'name' not in store_info or 'address' not in store_info or \
            'workdays_from' not in store_info or 'workdays_to' not in store_info or \
            'sat_from' not in store_info or 'sat_to' not in store_info or \
            'sun_from' not in store_info or 'sun_to' not in store_info:
        return None

    return store_info


def parse_item_info(line):
    item_info = {}
    attributes = line.split(' ')

    for attribute in attributes:
        if '=' in attribute:
            key, value = attribute.split('=')
            value = value.strip('"').strip("'")

            if key == "param":
                param_name = value.split(' ')[0]
                param_value = value.split(' ')[-1]

                if param_name not in item_info:
                    item_info[param_name] = []
                item_info[param_name].append(param_value)

            else:
                item_info[key] = value

    return item_info


def index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(form.cleaned_data['xml_upload'])
    else:
        form = UploadFileForm()
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def login(request):
    return render(request, 'login/login.html')

def terms(request):
    return render(request, 'main/terms.html')
