from collections import OrderedDict
import requests
from tqdm import tqdm
from argparse import FileType
import sys

import rest_framework

from django.core.management import BaseCommand
from webfront.views.cache import canonical

requests.adapters.DEFAULT_RETRIES = 5


def get_unique_lines(logfiles):
    files = tqdm(logfiles, unit="files", leave=True, desc="reading files")
    lut = OrderedDict()
    for file in files:
        with open(file, "r") as handle:
            for line in tqdm(
                handle, desc="reading {}".format(file), unit="lines", leave=False
            ):
                line = line.strip()
                if line and not line.startswith("#"):
                    line = canonical(line, remove_all_page_size=True)
                    lut[line] = lut.get(line, 0) + 1
    return sorted(lut, key=lut.get, reverse=True)


def send_query(url):
    return (
        # first request
        requests.get(url),
        # second request (to make sure it's in cache)
        requests.get(url),
    )


def stat_message(responses):
    return (
        # total request time
        responses[0].elapsed.total_seconds(),
        # return status code from the server
        responses[0].status_code,
        # URL for this request
        responses[0].url,
        # was the URL already in the cache somehow? (from previous run maybe?)
        responses[0].headers.get("Cached", "false"),
        # is the URL now in the cache?
        responses[1].headers.get("Cached", "false"),
    )


def send_queries(root, page_sizes, queries):
    wrapped = tqdm(unit="queries", desc="sending queries", total=len(queries))
    for query in queries:
        url = root + query
        wrapped.update()
        wrapped.set_description(url, True)
        try:
            responses = send_query(url)
            yield stat_message(responses)
            if responses[1].status_code is not rest_framework.status.HTTP_200_OK:
                continue
            # check to see if the result content contains an array of results
            # if so, we need to also trigger the caching for other page sizes
            results = responses[1].json().get("results")
            if results and len(results):
                for size in page_sizes:
                    extra_url = canonical(
                        "{}{}page_size={}".format(
                            url, "?" if url.endswith("/") else "&", size
                        )
                    )
                    wrapped.update()
                    wrapped.total += 1
                    wrapped.set_description(extra_url, True)
                    try:
                        responses = send_query(extra_url)
                        yield stat_message(responses)
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        print(e, file=sys.stderr)
                        raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e, file=sys.stderr)
            raise
    wrapped.set_description("sent all {} queries".format(wrapped.total), True)
    return


def analyze_stats(stats, n, output):
    stats.sort(key=lambda t: t[0], reverse=True)
    print(" - Here are the {} longest queries\n".format(n), file=sys.stderr)
    for (time, status, url, was_cached, is_cached) in stats[:n]:
        if time < 1:
            log_time = "{}ms".format(int(time * 1000))
        else:
            log_time = "{:.3f}s".format(round(time, 3))
        print(
            "{}: {}{}".format(log_time, url, " (was cached)" if was_cached else ""),
            file=sys.stderr,
        )
    print("time", "status", "url", "was cached", "got cached", sep="\t", file=output)
    failed = 0
    for (time, status, url, was_cached, is_cached) in stats:
        if status is not rest_framework.status.HTTP_200_OK:
            failed += 1
        print(time, status, url, was_cached, is_cached, sep="\t", file=output)
    if failed:
        print(
            "❌ {} URL{} failed to be processed".format(
                failed, "s" if failed > 1 else ""
            ),
            file=sys.stderr,
        )
    else:
        print("✅ all URLs were processed successfully", file=sys.stderr)
    return failed


def main(logfiles, root, page_sizes, top, output, *args, **kwargs):
    queries = get_unique_lines(logfiles)
    print("- Found {} unique URLs".format(len(queries)), file=sys.stderr)
    stats = list(send_queries(root, page_sizes, queries))
    return analyze_stats(stats, top, output)


class Command(BaseCommand):
    help = "warms up the API"

    def add_arguments(self, parser):
        parser.add_argument(
            "logfiles", type=str, nargs="+", help="log files with requests to execute"
        )
        parser.add_argument(
            "--root",
            "-r",
            type=str,
            help="URL root",
            default="http://wp-np3-ac.ebi.ac.uk/interpro7",
        )
        parser.add_argument(
            "--page_sizes",
            "-p",
            type=int,
            nargs="+",
            help="extra page size to query",
            default=[100, 50],
        )
        parser.add_argument(
            "--top",
            "-t",
            type=int,
            help="display the top n longest queries",
            default=10,
        )
        parser.add_argument(
            "--output",
            "-o",
            type=FileType("w"),
            help="output file for logs (defaults to stdout)",
            default=sys.stdout,
        )

    def handle(self, *args, **options):
        failed = main(**options)
        sys.exit(1 if failed else 0)
