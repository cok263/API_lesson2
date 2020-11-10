import requests
import os
import argparse
from dotenv import load_dotenv
from urllib.parse import urlparse


def cut_link(link):
    parse_link = urlparse(link)
    return parse_link.netloc + parse_link.path


def is_link_exist(token, link):
    headers = {
        'Authorization': 'Bearer {}'.format(token),
    }

    response = requests.get(
        'https://api-ssl.bitly.com/v4/bitlinks/{}'.format(cut_link(link)),
        headers=headers
    )
    if response.status_code == 404:
        return False
    else:
        response.raise_for_status()
        return True


def shorten_link(token, url):
    payload = {
        'long_url': url,
    }

    headers = {
        'Authorization': 'Bearer {}'.format(token),
    }

    response = requests.post(
        'https://api-ssl.bitly.com/v4/shorten', json=payload,
        headers=headers
    )
    response.raise_for_status()
    return response.json()['link']


def count_clicks(token, link):
    payload = {
        'unit': 'day',
        'units': -1,
    }

    headers = {
        'Authorization': 'Bearer {}'.format(token),
    }

    response = requests.get(
        'https://api-ssl.bitly.com/v4/bitlinks/{}/clicks/summary'
        .format(cut_link(link)),
        params=payload,
        headers=headers
    )
    response.raise_for_status()
    return response.json()['total_clicks']


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description='Программа возвращает количество переходов по укороченной ссылке, либо возвращает укороченную ссылку'
    )
    parser.add_argument('url', help='ссылка')
    args = parser.parse_args()

    url = args.url
    token = os.getenv("BITLY_TOKEN")

    try:
        is_link_exists_ = is_link_exist(token, url)
    except requests.exceptions.HTTPError:
        print('Не удалось проверить существование ссылки')
    else:
        if is_link_exists_:
            try:
                clicks_count = count_clicks(token, url)
            except requests.exceptions.HTTPError:
                print('Некорректный битлинк')
            else:
                print('Количество кликов:', clicks_count)
        else:
            try:
                bitlink = shorten_link(token, url)
            except requests.exceptions.HTTPError:
                print('Некорректная ссылка')
            else:
                print('Битлинк:', bitlink)


if __name__ == "__main__":
    main()
