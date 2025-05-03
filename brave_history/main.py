import argparse
import datetime
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse

HISTORY_PATH =  Path.home() / ".config" / "BraveSoftware" / "Brave-Browser" / "Default" / "History"

PARSER = argparse.ArgumentParser(description='Output brave history', epilog="By @readwithai  📖 https://readwithai.substack.com/ ⚡️ machine-aided reading")
PARSER.add_argument('--data-path', action='store_true', default=False)
PARSER.add_argument('--sqlite', action='store_true', default=False, help="Open the file with sqlite")
field_mx = PARSER.add_mutually_exclusive_group()
field_mx.add_argument('--title', action='store_true', default=False, help="Only display the title")
field_mx.add_argument('--url', action='store_true', default=False, help="Only display the title")
field_mx.add_argument('--json', help="Output results in json", action='store_true')
field_mx
PARSER.add_argument('--domain', help="Filter for this domain")
PARSER.add_argument('--path', help="Filter for this domain")
PARSER.add_argument('--today', help="Filter for this domain", action='store_true')
PARSER.add_argument('--hour', help="Filter for this domain", action='store_true')
PARSER.add_argument("filter", type=str, nargs='*')




def main():
    tmp = tempfile.NamedTemporaryFile()



    args = PARSER.parse_args()
    if args.data_path:
        print(HISTORY_PATH)
        return

    shutil.copy(HISTORY_PATH, tmp.name)
    try:

        if args.sqlite:
            subprocess.call(["sqlite3", tmp.name])
            return


        conn = sqlite3.connect(tmp.name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT u.url as url, title, v.visit_time as time FROM urls u JOIN visits v ON v.url=u.id ORDER BY v.visit_time desc')
        rows = cursor.fetchall()
        for row in rows:
            if args.filter:

                failed = False
                for x in args.filter:
                    if x in row["url"]:
                        continue

                    if x in row["title"]:
                        continue

                    if x in row["url"]:
                        continue

                    failed = True
                    break

                if failed:
                    continue


            info = urlparse(row["url"])
            if args.domain:
                if not domain_prefix(args.domain, info.netloc):
                    continue

            if args.path:
                if info.path != args.path:
                    continue


            # print(row["time"])
            # print(datetime.datetime.fromtimestamp(row["time"] / 1e9))
            # https://stackoverflow.com/questions/20458406/what-is-the-format-of-chromes-timestamps

            dt = (datetime.datetime.fromtimestamp(row["time"] / 1e6 - 11644473600))

            timestamp = format_dt(dt)

            if args.today:
                today_start = datetime.datetime.now(datetime.UTC).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
                print(dt.isoformat(), today_start.isoformat())
                if dt < today_start:
                    continue




            try:
                if args.title:
                    print(timestamp, row["title"])
                elif args.url:
                    print(timestamp, row["url"])
                elif args.json:
                    print(json.dumps(dict(timestamp=dt.isoformat(), url=row["url"], host=info.netloc)))
                else:
                    print(timestamp, row["url"], row["title"])
            except BrokenPipeError:
                break
        conn.close()
    finally:
        os.unlink(tmp.name)


def format_dt(dt):
    # Round to a tenth ofa second
    microseconds = (dt.microsecond + 5000) // 10000 * 10000
    if microseconds == 1000000:
        return (dt + datetime.timedelta(seconds=1)).replace(microsecond=0)
    else:
        return dt.replace(microsecond=microseconds).isoformat()[:-4]

def domain_prefix(prefix, url):
    prefix = prefix.split(".")
    url = url.split(".")
    return url[-len(prefix):] == prefix
