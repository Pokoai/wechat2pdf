#! python
# find_all_links.py - 通过合集链接找到该合集下所有文章的ID、标题、链接、序列号、发布时间等信息

"""
功能基本实现 2022-7-4

"""

import requests, bs4
import re
import os



# 爬取合集名称、id、文章数量以及公众号名称等信息
def get_album_info(album_url):
    """
    :param album_url: 合集链接
    :return: 合集名称, 合集文章数量, 合集id, _biz唯一标识,
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    }
    res = requests.get(album_url, headers)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")

    # 获取微信公众号名称
    wechat_name_elem = soup.select('.album__author-name')
    wechat_name = wechat_name_elem[0].getText()

    # 获取合集名称
    album_name_elem = soup.select('#js_tag_name')
    album_name = album_name_elem[0].getText().replace('#', '')

    # 获取合集文章数量
    album_num_elem = soup.select('.album__num')
    album_post_nums = int(album_num_elem[0].getText().split('个')[0])  # 27个内容，提取27

    # 从第一篇文章的 link 里提取出 _biz 唯一用户标识， 供 set_params 使用
    first_post_elem = soup.select('li')[0]
    link = first_post_elem.get('data-link')
    _biz = re.search(r'__biz=(\S+)&mid', link).group(1)

    # 从手动提供的 album_url 中提取出 album_id，供 set_params 使用
    album_id = re.search(r'album_id=(\d+)&', album_url).group(1)

    return album_name, album_post_nums, album_id, _biz



# 单独爬取合集页面里第一篇（倒序）文章ID、标题、链接、序列号、发布时间
# 顺便爬取微信公众号名称、合集名称
# 将以上内容写入文件data.txt中，后续可改为写入数据库中或csv
# 同时返回第一篇文章id、data.txt文件夹路径、合集文章数量、公众号唯一标识_biz
def get_first_post_info(album_url, album_post_nums):
    """
    :param album_url: 合集链接
    :param album_post_nums: 合集文章数量， 给第一篇文章设置序列号
    :param output_dir_path: 最外层文件夹（D:\Media\Desktop\wechat2pdf）
    :return:
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    }
    res = requests.get(album_url, headers)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")

    first_post_elem = soup.select('li')[0]

    ### 以下信息都是从合集链接的requests.get(album_url, headers) 获取的，为了消除重复代码，可以改为从requests.get(link, headers)获取 ###
    # 文章序列号
    post_num = first_post_elem.get('data-pos_num')
    # 有的合集文章没有设置 pos_num 属性，爬取不到。但是第一篇文章的序列号与合集文章数量相同，所以以此设置。
    if post_num == '':
        post_num = str(album_post_nums)

    # 文章标题
    title = first_post_elem.get('data-title')
    # 文章链接
    link = first_post_elem.get('data-link')
    # 文章id
    first_post_id = first_post_elem.get('data-msgid')
    ### 以上信息都是从合集链接的requests.get(album_url, headers) 获取的，为了消除重复代码，可以改为从requests.get(link, headers)获取 ###

    # 获取文章发布时间
    # 但是发布时间是用 JavaScript 渲染后显示的，需要用正则表达式截取时间戳，然后转换
    # ![](https://img.arctee.cn/one/202207021312051.png)
    publish_time = 0  # 设置发布时间默认值为0
    res_post = requests.get(link, headers)
    res_post.raise_for_status()

    match = re.search(r'\{e\(0,(.*),0,document.getElementById\("publish_time"\)\)', res_post.text, re.S)
    if match:
        publish_time = int(match.group(1).split('"')[1])

    return post_num, title, link, publish_time, first_post_id



# 设置合集文件夹路径、数据库文件路径，并新建文件夹和文件
def set_album_db_path(album_name, output_path):
    """
    :param album_name: 合集名称
    :param output_path: 最外层文件夹路径，需要自己指定
    :return: 合集路径、数据库文件路径
    """
    # 合集文件夹路径
    album_path = os.path.join(output_path, album_name)

    # 若合集文件夹不存在，则新建，否则忽略
    os.makedirs(album_path, exist_ok=True)

    # 数据库 data.txt 文件路径
    db_path = os.path.join(album_path, 'data.txt')

    return album_path, db_path



# 设置 requests.get() 参数params
def set_params(album_id, begin_id, _biz):
    """
    :param first_id: 第一篇文章id，合集主页爬取所得
    :param album_id: 合集id
    :param _biz: 唯一用户标识，合集主页爬取所得
    :return:
    """
    params = {
        'action': 'getalbum',
        '_biz': _biz,
        'album_id': album_id,
        'count': '20',
        'begin_msgid': str(begin_id),
        'begin_itemidx': '1',
        'uin': '',
        'key': '',
        'pass_ticket': '',
        'wxtoken': '',
        'devicetype': '',
        'clientversion': '',
        '_biz': _biz,
        'appmsg_token': '',
        'x5': '0',
        'f': 'json',
    }
    return params



# 向数据库文件 data.txt 写入文章信息
def write2db(db_path, flag, pos_num, title, publish_time, link, post_id):
    """
    :param db_path: 数据库路径
    :param pos_num: 文章序列号
    :param title: 文章标题
    :param publish_time: 发布时间
    :param link: 文章链接
    :param post_id: 文章id
    :param flag: 1->第一篇文章，0->其他文章
    :return:
    """
    if 1 == flag:
        mode = 'w'
    else:
        mode = 'a+'

    with open(db_path, mode, encoding='utf-8') as f:
        f.write(f'序列：{pos_num}\n文章标题：{title}\n发布时间：{publish_time}\n'
                f'链接：{link}\nID：{post_id}\n\n')



# 爬取合集内除第一篇文章外，其他文章的标题、链接、发布时间、ID等信息
def get_rest_post_info(first_post_id, album_id, _biz, album_post_nums, db_path):
    """
    album_url：合集链接
    output_dir_path：存储文章信息的文件所在文件夹
    """

    post_max_num = album_post_nums-1  # 第一篇文章已经单独爬取过，这里从第二篇开始，故文章序列号从（album_post_nums-1）开始
    get_post_nums = 1  # 总共爬取到的文章数量。第一篇已经单独爬取过，所以起始为1
    post_cnt = 0  # 每一次循环爬取到的文章数量

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    }
    # 通过网络抓包获取的url
    url = 'https://mp.weixin.qq.com/mp/appmsgalbum'

    begin_id = first_post_id  # 初始化为第一篇文章id
    while True:
        # 获取服务器响应信息，起始id是第一篇的，所以返回的信息不包括第一篇，是从第二篇开始
        params = set_params(album_id, begin_id, _biz)
        data_json = requests.get(url=url, headers=headers, params=params).json()
        # print(data_json)

        # 解析返回的 json数据
        album_resp = data_json.get('getalbum_resp')
        post_list = album_resp.get('article_list')
        # print(post_list)
        # 一共就两篇文章时，以第一篇id为起点去爬取，返回的就只要一篇文章信息，那么post_list是一个单层字典
        if (1 == post_max_num):
            post_num = str(post_max_num)  # 文章序列号
            title = post_list['title']  # 文章标题
            link = post_list['url']  # 文章链接
            publish_time = post_list['create_time']  # 文章发布时间
            post_id = post_list['msgid']  # 文章id

            # 将文章信息写入 data.txt 数据库
            write2db(db_path, 0, post_num, title, publish_time, link, post_id)
            break
        else:  # 多于2篇文章
            for dic in post_list:
                title = dic['title']    # 文章标题
                link = dic['url']       # 文章链接
                publish_time = dic['create_time']  # 文章发布时间
                post_id = dic['msgid']  # 文章id

                # 有的合集文章没有设置 pos_num 属性，爬取不到，故需要自己设置
                if 'pos_num' in dic:
                    post_num = dic['pos_num']
                else:
                    post_num = str(post_max_num)
                    post_max_num -= 1

                post_cnt += 1  # 更新 post_cnt
                # 将文章信息写入 data.txt 数据库
                write2db(db_path, 0, post_num, title, publish_time, link, post_id)
            get_post_nums += post_cnt  # 更新 get_post_nums

            # 如果本次最后一篇文章的 post_num 为 1 则跳出循环
            # if int(post_list[post_cnt-1]['pos_num']) == 1:
            # 该退出循环条件有问题，因为某些合集 pos_num 为空

            # 现换为 get_post_nums == album_post_nums 作为退出条件，
            # 即爬取获得的文章数量等于该合集文章数量（已知），则说明已经全部爬取完了，那么就结束
            if get_post_nums == album_post_nums:
                break

            # 每次响应最多只返回20篇文章的信息，所以要找到本次响应的最后一篇文章，
            # 以它的id作为下一次起始id
            begin_id = post_list[post_cnt-1]['msgid']  # 更新 begin_id
            post_cnt = 0  # post_cnt 需要清零，为下次循环准备



# 最新想法（2022-7-12）：不从这里入手去实现增量更新，因为从这里入手的话，新的data.txt会覆盖掉旧的，
# 那么data.txt里面就只有一篇文章信息，不符合数据库文件的功能（即记录所有信息）
# 现在想到一个新思路：从 wechat2pdf()最终转化pdf的函数去入手，提供一个新版本，
# 每天只下载第一个链接的文章，后续每天运行时采用该版本，仅爬取最新一篇文章。
# 目前程序组织很简单，没有软件工程的思想，能自己用起来就行。以后再考虑重构。


# 更新数据库文件（非增量更新，以后可改进）
def update_db(album_url, output_path):
    # 获取合集信息
    album_info = get_album_info(album_url)  # (album_name, album_post_nums, album_id, _biz)
    # print(album_info)
    album_name = album_info[0]
    album_post_nums = album_info[1]
    album_id = album_info[2]
    _biz = album_info[3]

    # 设置合集路径、数据库路径
    album_path, db_path = set_album_db_path(album_name, output_path)

    # 先将第一篇文章信息写入数据库文件data.txt
    post_num, title, link, publish_time, first_post_id = \
        get_first_post_info(album_url, album_post_nums)
    # print(db_path + '\n' + str(post_num) + '\n' +  title + '\n'  + str(publish_time)  + '\n'  + link + '\n' + first_post_id)
    write2db(db_path, 1, post_num, title, publish_time, link, first_post_id)

    # 如果合集只有一篇文章，则不用执行 get_rest_info()
    # print(album_post_nums)
    if album_post_nums > 1:
        # 再将剩余文章信息写入数据库文件data.txt
        get_rest_post_info(first_post_id, album_id, _biz, album_post_nums, db_path)

    return album_path, db_path


if __name__ == "__main__":
    album_url = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2467166481575985152&scene=173&from_msgid=2653411345&from_itemidx=1&count=3&nolastread=1#wechat_redirect"
    output_path = "D:\Media\Desktop\wechat2pdf"

    update_db(album_url, output_path)

    print("\n数据库更新完成!")