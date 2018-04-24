from collections import OrderedDict
import requests
from tqdm import tqdm

requests.adapters.DEFAULT_RETRIES = 5

from django.core.management import BaseCommand
from webfront.views.cache import canonical

def get_unique_lines(logfiles):
    files = tqdm(logfiles, unit="files", leave=True, desc="reading files")
    lut = OrderedDict()
    for file in files:
        with open(file, "r") as handle:
            for line in tqdm(handle, desc="reading {}".format(file), unit="lines", leave=False):
                line = line.strip()
                if line:
                    line = canonical(line, remove_all_page_size=True)
                    lut[line] = lut.get(line, 0) + 1
    return sorted(lut, key=lut.get, reverse=True)

def send_query(url):
    return requests.get(url)

def send_queries(root, page_sizes, queries):
    times = []
    wrapped = tqdm(unit="queries", desc="sending queries", total=len(queries))
    for query in queries:
        url = root.format(query)
        wrapped.update()
        wrapped.set_description(url, True)
        try:
            response = send_query(url)
            times.append((response.elapsed.total_seconds(), url))
            results = response.json().get('results')
            if results and len(results):
                for size in page_sizes:
                    extra_url = canonical(
                        '{}{}page_size={}'.format(
                            url,
                            '?' if url.endswith('/') else '&',
                            size
                        )
                    )
                    wrapped.update()
                    wrapped.total += 1
                    wrapped.set_description(extra_url, True)
                    try:
                        response = send_query(extra_url)
                        times.append((response.elapsed.total_seconds(), extra_url))
                    except KeyboardInterrupt:
                        raise
                    except:
                        pass
        except KeyboardInterrupt:
            raise
        except:
            pass
    wrapped.set_description('sent all {} queries'.format(wrapped.total), True)
    return times

def print_stats(times, n):
    times.sort(key=lambda t: t[0], reverse=True)
    print(' - Here are the {} longest queries'.format(n))
    for (time, url) in times[:n]:
        if time < 1:
            log_time = '{}ms'.format(int(time * 1000))
        else:
            log_time = '{:.3f}s'.format(round(time, 3))
        print('{}: {}'.format(log_time, url))

def main(logfiles, root, page_sizes, top, *args, **kwargs):
    queries = get_unique_lines(logfiles)
    print('- Found {} unique URLs'.format(len(queries)))
    times = send_queries(root, page_sizes, queries)
    print_stats(times, top)

class Command(BaseCommand):
    help = "warms up the API"

    def add_arguments(self, parser):
        parser.add_argument(
            "logfiles", type=str, nargs="+",
            help="log files with requests to execute"
        )
        parser.add_argument(
            "--root", "-r", type=str, nargs=1,
            help="URL root", default="http://wp-np3-ac.ebi.ac.uk/interpro7{}"
        )
        parser.add_argument(
            "--page_sizes", "-p", type=int, nargs="+",
            help="extra page size to query", default=[100, 50]
        )
        parser.add_argument(
            "--top", "-t", type=int, nargs=1,
            help="display the top n longest queries", default=10
        )

    def handle(self, *args, **options):
        main(**options)
