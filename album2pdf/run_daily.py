#! python
# run_daily.py - 每天遍历合集列表，然后自动下载最新文章

import re, time, os

from album2pdf_v1 import wechat2pdf
from find_all_links import get_first_post_info
from find_all_links import update_db
from update_logs import read_logs, get_update_status, update_logs
from mail import send_email
from wechat_notice import wechat_group_notice


######################## 需要自己提供的 ############################################
# 自己感兴趣的合集链接
album_dict = {
    '日记': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2461687967875416065&scene=173&from_msgid=2653411356&from_itemidx=1&count=3&nolastread=1#wechat_redirect",
    '长赢指数投资计划': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2467166481575985152&scene=173&from_msgid=2653411345&from_itemidx=1&count=3&nolastread=1#wechat_redirect",
    '孟岩投资实证（2022）': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIzNTQ4ODg4OA==&action=getalbum&album_id=2206783352551063553&scene=173&from_msgid=2247487451&from_itemidx=1&count=3&nolastread=1#wechat_redirect",

}
# 合集名称数据
album_name_list = list(album_dict.keys())
# 最外层文件夹地址
output_path = "D:\Media\Desktop\wechat2pdf"
# 日志路径
logs_path = os.path.join(output_path, '更新日志.txt')
#################################################################################


# 更新所有合集 data.txt 数据库文件
def update_all_db(album_dict):
    print("###################### 开始更新：数据库 ######################")
    for album in album_dict.items():
        album_url = album[1]
        print(f"----------- 正在更新：{album[0]}合集 数据库 -----------")
        update_db(album_url, output_path)
    print("###################### 完成更新：数据库 ######################")


# # 下载所有合集所有文章
# def down_all_album():
#     for album in album_url_dict.items():
#         album_url = album[1]

#         print(f"\n################### 开始下载 「{album[0]}合集」 ###################\n")
#         wechat2pdf(album_url, output_path, 0)  # 下载所有文章
#     print("\n####################### 所有合集增量下载完成 #######################\n")


# 下载已更新的合集的最新文章
# 因为公众号每天只能发布一篇文章，所以只要运行一次 down_all_album，以后每天运行 down_update_album 即可保持文章同步更新
def down_update_album(album_dict, update_flg):
    album_list = list(album_dict.items())

    for i in range(len(update_flg)):
        if update_flg[i] == 1:  # 标志位为1才下载
            album_url = album_list[i][1]

            print(f"\n################### 开始下载 「{album_list[i][0]}合集」 ###################\n")
            wechat2pdf(album_url, output_path, 1)  # 仅下载第一篇文章
    print("\n####################### 所有合集增量下载完成 #######################")



def run_daily():
    start_time = time.time()

    # 1. 更新所有合集 data.txt 数据库文件
    update_all_db(album_dict)

    # 2. 更新日志文件，并获取更新标志位、更新文章数量
    update_flg, update_cnt, logs = update_logs(logs_path, output_path, album_name_list)

    # 3. 增量下载文章，如果所有合集均未发布新文章，则不用下载
    if 1 in update_flg:
        down_update_album(album_dict, update_flg)

        end_time = time.time()
        all_time = int(end_time - start_time)

        print(f"\n本次更新状态：\n共更新 {update_cnt} 篇文章！")
        print(f"总耗时：{all_time}秒")
        print(f"敬请阅读！")
    else:
        print("\n本次更新状态：\n所有合集没有新文章，无需下载！")

    # 4. 有更新则发送邮件通知
    if update_cnt > 0:  # 该执行代码块可以合并到上面去，但是为了区分开功能，故又重复判断了一次是否有文中更新，只是换了一种方法：update_cnt > 0
        send_email(logs)

        wechat_group_notice(logs)

    wechat_group_notice(logs)
    # send_email(logs)
    # 运行该程序时新生成的日志数据无法读取到，猜测是只有程序运行完才会将更新内容从缓存区写入文件中，
    # 暂时只能采取折中方案：将send_email作为另一个进程运行。

    # 找到解决方案：https://blog.csdn.net/foreverhjhjhj/article/details/51658446
    # 经测试，上面方案无效
    # 最终通过 mail.py 读取日志文件时首先添加一句 f_log.seek(0) 解决问题
    # 经测试，上面方案最终也无效。暂时不知道问题出在哪里
    # 所以换一种方案，邮件内容不去读取日志文件，而是直接采用 update_logs.py 中 get_update_status函数产生的logs数组


if __name__ == "__main__":
    run_daily()