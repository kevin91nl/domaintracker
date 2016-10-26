import argparse
import threading
from itertools import product
import pythonwhois
import datetime
import re
import os
import time

from pythonwhois.shared import WhoisException


def is_free(domain):
    """
    Check whether a domain is free. For example:

    >>> is_free('www.google.com')

    :param domain: The domain to check.
    :return: True if the domain is free, False if the domain is not free and None if the status is unknown.
    """
    try:
        details = pythonwhois.get_whois(domain)
    except UnicodeDecodeError:
        return None
    except WhoisException:
        return None
    # If any experiation date is set after today, then the domain is definitely not free
    if 'expiration_date' in details.keys():
        for expiration_date in details['expiration_date']:
            if expiration_date > datetime.datetime.now():
                return False
    return details['contacts']['registrant'] is None


def process_website(website, output, lock, attempts):
    """
    Process a website (in a different thread).

    :param website: Website to parse.
    :param output: 'STD' or filename (for CSV output).
    :param lock: Write lock for the output.
    :param attempts: Number of attempts tried.
    """
    if attempts >= 3:
        return
    try:
        domain_free = is_free(website)
    except ConnectionResetError:
        time.sleep(2 ** attempts)
        return process_website(website, output, lock, attempts + 1)
    if domain_free:
        lock.acquire()
        if output == 'STD':
            print(website)
        else:
            first_item = not os.path.exists(output)
            with open(output, 'a') as file_handle:
                if not first_item:
                    file_handle.write(';')
                file_handle.write(website)
        lock.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check the availability of domains.')
    parser.add_argument('request', help='The domains to check the availability for.')
    parser.add_argument('-o', '--output', help='Output the results to a CSV file specified by this argument.',
                        default='STD')
    args = parser.parse_args()
    request = args.request
    output = args.output

    if os.path.exists(output):
        os.remove(output)

    request = re.sub(r'\s+', '', request)
    pattern = re.compile(r'[(]{1}([^()]+)[)]')
    factors = []
    for group in re.findall(pattern, request):
        items = group.split(',')
        factors.append(items)
    websites = list(product(*factors))

    threads = []
    lock = threading.Lock()
    for website_count, website in enumerate(websites):
        website = ''.join(website)
        thread = threading.Thread(target=process_website, args=(website, output, lock, 1))
        thread.daemon = True
        thread.start()
        threads.append(thread)
        if website_count % 50 == 0:
            for thread in threads:
                thread.join()
            print('Progress: %d / %d' % (website_count + 1, len(websites)))
            threads = []

    for thread in threads:
        thread.join()
