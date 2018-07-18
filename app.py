#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import requests
import shutil
from bs4 import BeautifulSoup


base_dir = ''
site_url = ''
site_path = ''

visited_links = []
error_links = []


def init_env():
    global base_dir
    global site_url
    global site_path
    try:
        base_dir = os.getcwd()
        site_url = sys.argv[1]
        site_path = sys.argv[2]
        if not site_url.endswith('/'):
            site_url += '/'
        if not site_path.endswith('/'):
            site_path += '/'
        os.makedirs(site_path, exist_ok=True)

    except IndexError:
        print('Usage:\npython app.py www.example.com folder_name')
        sys.exit(1)


def save(bs, element, check):
    links = bs.find_all(element)

    for l in links:
        if element == 'link':
            href = l.get('href')
        elif element == 'script':
            href = l.get('src')

        if href is not None and href not in visited_links:
            if href.startswith('http'):
                print('+++ HREF: %s' % (href))
                if not site_url in href:
                    continue
            #else:
            #    print('href: %s' % (href))
            if check in href:
                print('Working with : {}'.format(href))
                if '//' in href:
                    path_s = href.split('/')
                    file_name = ''
                    for i in range(3, len(path_s)):
                        file_name = file_name + '/' + path_s[i]
                else:
                    file_name = href

                l = site_url + file_name
                #print('link: %s' % (l))
                #continue

                try:
                    r = requests.get(l)
                except requests.exceptions.ConnectionError:
                    error_links.append(l)
                    continue

                if r.status_code != 200:
                    error_links.append(l)
                    continue

                os.makedirs(os.path.dirname(site_path + file_name.split('?')[0]), exist_ok=True)
                with open(site_path + file_name.split('?')[0], 'wb') as f:
                    f.write(r.text.encode('utf-8'))
                    f.close()

                visited_links.append(l)


def save_assets(html_text):
    bs = BeautifulSoup(html_text, 'html.parser')
    save(bs=bs, element='link', check='.css')
    save(bs=bs, element='script', check='.js')

    links = bs.find_all('img')
    for l in links:
        href = l.get('src')
        if href is not None and href not in visited_links:
            print('Working with : {}'.format(href))
            if '//' in href:
                path_s = href.split('/')
                file_name = ''
                for i in range(3, len(path_s)):
                    file_name = file_name + '/' + path_s[i]
            else:
                file_name = href

            l = site_url + file_name
            ## print('link: %s => %s [%s]' % (l, file_name, file_name.split('?')[0]))
            ## continue

            try:
                r = requests.get(l, stream=True)
            except requests.exceptions.ConnectionError:
                error_links.append(l)
                continue

            if r.status_code != 200:
                error_links.append(l)
                continue

            os.makedirs(os.path.dirname(site_path + file_name.split('?')[0]), exist_ok=True)
            with open(site_path + file_name.split('?')[0], 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            visited_links.append(l)


def crawl(link):
    if 'http://' not in link and 'https://' not in link:
        link = site_url + link

    if site_url in link and link not in visited_links:
        print('Working with : {}'.format(link))

        path_s = link.split('/')
        file_name = ''
        for i in range(3, len(path_s)):
            file_name = file_name + '/' + path_s[i]

        if file_name[len(file_name) - 1] != '/':
            file_name = file_name + '/'
        if file_name.startswith('/#'):
            return()
            print("--- %s" % (file_name))
        elif file_name.startswith('/phpbb'):
            return()
            print("--- %s" % (file_name))
        elif file_name.startswith('/downloads/images/'):
            return()
            print("--- %s" % (file_name))
        else:
            print("*+++ %s" % (file_name))

        try:
            r = requests.get(link)
        except requests.exceptions.ConnectionError:
            print('Connection Error')
            sys.exit(1)

        if r.status_code != 200:
            print('Invalid Response')
            sys.exit(1)
        print(site_path + file_name + 'index.html')
        os.makedirs(os.path.dirname(site_path + file_name.split('?')[0]), exist_ok=True)
        with open(site_path + file_name.split('?')[0] + 'index.html', 'wb') as f:
            text = r.text.replace(site_url, site_path)
            f.write(text.encode('utf-8'))
            f.close()

        visited_links.append(link)

        save_assets(r.text)

        soup = BeautifulSoup(r.text, 'html.parser')

        for link in soup.find_all('a'):
            try:
                crawl(link.get('href'))
            except:
                error_links.append(link.get('href'))


def gogo():
    crawl(site_url)
    print('Link crawled\n')
    for link in visited_links:
        print('--- {}'.format(link))
    
    print('\n\nLink error\n')
    for link in error_links:
        print('--- {}'.format(link))


if __name__=='__main__':
    if (len(sys.argv) < 3):
        sys.exit()
    init_env()
    print('base_dir :%s' % (base_dir ))
    print('site_url :%s' % (site_url ))
    print('site_path:%s' % (site_path))
    gogo()
    sys.exit()
