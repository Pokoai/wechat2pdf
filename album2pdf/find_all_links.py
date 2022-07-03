#! python
# find_all_links.py - 通过合集链接找到该合集下所有文章的链接、标题等信息

import requests, bs4
import os

# 设置requests.get()的参数params
# 目前仅自动获取first_id, 其他参数手动提供，后续改进为全部自动获取
def set_params(first_id):
    params = {
        'action': 'getalbum',
        '_biz': 'MzIzNTQ4ODg4OA==',
        'album_id': '2206783352551063553',
        'count': '20',
        'begin_msgid': str(first_id),
        'begin_itemidx': '1',
        'uin': '',
        'key': '',
        'pass_ticket': '',
        'wxtoken': '',
        'devicetype': '',
        'clientversion': '',
        '_biz': 'MzIzNTQ4ODg4OA==',
        'appmsg_token': '',
        'x5': '0',
        'f': 'json',
    }
    return params

# 获取合集内所有文章标题、链接、发布时间、ID等信息
def get_all_info(url, output_dir_path):
    """
    url：合集链接
    output_dir_path：存储文章信息的文件所在文件夹
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    }

    # 先获取最新文章ID
    res = requests.get(url, headers)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text)
    firstIdElem = soup.select('li')[0]
    first_id = firstIdElem.get('data-msgid')  # 合集页面里排在第一位的文章id
    # print(first_id)

    # 通过网络抓包获取的urll
    urll = 'https://mp.weixin.qq.com/mp/appmsgalbum'
    params = set_params(first_id)
    data_json = requests.get(url=urll, headers=headers, params=params).json()

    # 这里应该将获取的数据写到csv文件中或者数据库里
    # 我暂时先写到data.txt文件里
    file_path = os.path.join(output_dir_path, 'data.txt')
    msg_cnt = 0  # 记录爬取到的文章数量

    # 解析返回的json数据
    album_resp = data_json.get('getalbum_resp')
    article_list = album_resp.get('article_list')
    for dic in article_list:
        pos_num = dic['pos_num']
        title = dic['title']
        # print(title)
        url = dic['url']
        create_time = dic['create_time']
        msgid = dic['msgid']
        msg_cnt += 1
    # print(msg_cnt)

        # 写入的文章不含最新的第一篇，也可能不包含最后的几篇
        with open(file_path, 'a+', encoding='utf-8') as f:
            f.write(f'序列：{pos_num}\n文章标题：{title}\n发布时间：{create_time}\n链接：{url}\nID：{msgid}\n\n')

    # 检查最后一篇文章的pos_num是否为1来判断爬取的文章是否齐全
    # 不为1则从new_id接着爬取，这里仅爬取两次，改进版可以通过循环检测爬取
    if int(article_list[msg_cnt-1]['pos_num']) != 1:
        new_id = article_list[msg_cnt-1]['msgid']
        first_id = new_id
        params = set_params(first_id)
        data_json = requests.get(url=urll, headers=headers, params=params).json()

        album_resp = data_json.get('getalbum_resp')
        article_list = album_resp.get('article_list')
        # msg_cnt += len(article_list)  # 总共爬取到的文章数量
        for dic in article_list:
            pos_num = dic['pos_num']
            title = dic['title']
            url = dic['url']
            create_time = dic['create_time']
            msgid = dic['msgid']

            with open(file_path, 'a+', encoding='utf-8') as f:
                f.write(f'序列：{pos_num}\n文章标题：{title}\n发布时间：{create_time}\n链接：{url}\nID：{msgid}\n\n')


if __name__ == "__main__":
    url = 'https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIzNTQ4ODg4OA==&action=getalbum&album_id=2206783352551063553&scene=173&from_msgid=2247487451&from_itemidx=1&count=3&nolastread=1#wechat_redirect'
    output_dir_path = "D:\Media\Desktop\wechat2pdf"  # 主文件夹路径
    get_all_info(url, output_dir_path)

    print("Done!")