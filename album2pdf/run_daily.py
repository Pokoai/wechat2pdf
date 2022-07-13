#! python
# run_daily.py - 每天遍历合集列表，然后自动下载最新文章

import re, time, os

from album2pdf_v1 import wechat2pdf
from find_all_links import get_first_msg_info
from find_all_links import get_all_info
from update_logs import get_history_nums, get_update_status, update_logs


# 自己感兴趣的合集链接
album_url_dict = {
    '日记': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2461687967875416065&scene=173&from_msgid=2653411356&from_itemidx=1&count=3&nolastread=1#wechat_redirect",
    '长赢指数投资计划': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2467166481575985152&scene=173&from_msgid=2653411345&from_itemidx=1&count=3&nolastread=1#wechat_redirect",
    '孟岩投资实证（2022）': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIzNTQ4ODg4OA==&action=getalbum&album_id=2206783352551063553&scene=173&from_msgid=2247487451&from_itemidx=1&count=3&nolastread=1#wechat_redirect",

}
# 合集名称数据
album_name_list = list(album_url_dict.keys())
# 最外层文件夹地址
output_dir_path = "D:\Media\Desktop\wechat2pdf"
# 日志路径
logs_path = os.path.join(output_dir_path, '更新日志.txt')


# 更新所有合集 data.txt 数据库文件
def update_all_db(album_url_dict):
    print("################### 开始更新：数据库data.txt ###################")
    for album in album_url_dict.items():
        album_url = album[1]
        print(f"----------- 正在更新：{album[0]}合集 数据库 -----------")
        get_all_info(album_url, output_dir_path)
    print("################# 更新完成：所有数据库data.txt  #################")


# # 下载所有合集所有文章
# def down_all_album():
#     for album in album_url_dict.items():
#         album_url = album[1]
#         # album_id = re.search(r'album_id=(\d+)&', album_url).group(1)  # 通过链接提取合集id
#         # print(f'\nalbum_id：{album_id}\n')
#         print(f"\n################### 开始下载 「{album[0]}合集」 ###################\n")
#         wechat2pdf(album_url, output_dir_path)
#     print("\n####################### 所有合集增量下载完成 #######################\n")


# 仅下载已更新的合集的最新文章
# 因为公众号每天只能发布一篇文章，所以只要运行一次 down_all_album，以后每天运行 down_update_album 即可保持文章同步更新
def down_update_album(album_url_dict, update_flg):
    album_list = list(album_url_dict.items())
    # print(type(album_list))

    for i in range(len(update_flg)):
        if update_flg[i] == 1:  # 标志位为1才启动下载，否则跳过
            album_url = album_list[i][1]
            # print(type(album_url))
            print(f"\n################### 开始下载 「{album_list[i][0]}合集」 ###################\n")
            wechat2pdf(album_url, output_dir_path)
    print("\n####################### 所有合集增量下载完成 #######################")



if __name__ == "__main__":
    start_time = time.time()

    # 1. 找到合集所有链接，更新所有合集 data.txt 数据库文件
    update_all_db(album_url_dict)

    # 2. 读取日志文件，与各合集数据库文件对比，获取更新状态
    logs, update_flg, update_cnt = get_update_status(
        output_dir_path, album_name_list, get_history_nums(logs_path))
    # print(update_flg)

    # 3. 更新日志 update_logs.txt 文件
    update_logs(logs, logs_path)

    # 4. 增量下载文章，但时如果所有合集均未发布新文章，则不用下载
    if 1 in update_flg:
        down_update_album(album_url_dict, update_flg)

        end_time = time.time()
        all_time = int(end_time - start_time)

        print(f"\n本次更新状态：\n共更新 {update_cnt} 篇文章！")
        print(f"总耗时：{all_time}秒")
        print(f"敬请阅读！")
    else:
        print("\n本次更新状态：\n所有合集没有新文章，无需下载！")

