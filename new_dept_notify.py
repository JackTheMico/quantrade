# -*- coding:utf-8 -*-
"""
-------------------------------------------------

    File Name:        quantrade/new_dept_notify.py

    Description:      打新债通知脚本，每个工作日执行一次，有新债则通过
                      server酱发送微信通知。

    Author:           jack@fireworkhq.com

    Date:             2021-09-21-13:12:56

    Version:          v1.0

    Lastmodified:     2021-09-21-13:12:56 by Jack Deng

-------------------------------------------------
"""

import re
import json
import requests
from datetime import date, datetime

url = "https://data.eastmoney.com/kzz/default.html"
notify_url = "https://sctapi.ftqq.com/{}.send"
receivers = [
    "SCT77574TpwHo7JJ1rMldsefaQFoV7xvt",
    "SCT77648TCvaviiUkbMC8sKb1KHMsF0RD"
]

def notify(title, message):
    data = {
        "title": title,
        "desp": message
    }
    for each in receivers:
        final_url = notify_url.format(each)
        requests.post(final_url, data=data)
    print("消息发送完毕")


def parse_dept(dept):
    res = {}
    res['债券代码'] = dept['SECURITY_CODE']
    res['债券名称'] = dept['SECURITY_NAME_ABBR']
    res['正股代码'] = dept['CONVERT_STOCK_CODE']
    res['正股名称'] = dept['SECURITY_SHORT_NAME']
    res['评级'] = dept['RATING']
    res['利率'] = dept['INTEREST_RATE_EXPLAIN']
    res['中签率'] = dept['ONLINE_GENERAL_LWR']
    res['申购日期'] = dept['PUBLIC_START_DATE'].split(" ")[0]
    res['中签号发布日'] = dept['BOND_START_DATE'].split(" ")[0]
    return res


def make_msg(data, delta):
    days = delta.days
    info = parse_dept(data)
    msg = "".join([f"##  {k}: {v}\n\n" for k, v in info.items()])
    if -3 <= days < 0:
        title = f"还有{int(days)}天即可打新债"
    elif days == 0:
        title = f"今天即可打新债"
    else:
        title = f"无新债可打"
        msg = ""
    return title, msg


def main():
    res = requests.get(url)
    target = re.search(r'var\s+pagedata=\s+(.*);', res.text).group(1)
    json_res = json.loads(target)
    data = json_res['list']['result']['data']
    newest = data[0]
    start_date_str = newest['PUBLIC_START_DATE']
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S") 
    now_date = datetime.now()
    delta = now_date - start_date
    # debug
    # delta = start_date - start_date
    title, msg = make_msg(newest, delta)
    notify(title, msg)


if __name__ == '__main__':
    main()
