#! python
# run_daily.py - 每天遍历合集列表，然后自动下载最新文章

import re, time

from album2pdf_v1 import wechat2pdf
from find_all_links import get_first_msg_info

# (album_url, output_dir_path):

# 自己感兴趣的合集链接
album_url_dict = {
    'E大日记合集': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2461687967875416065&scene=173&from_msgid=2653411356&from_itemidx=1&count=3&nolastread=1#wechat_redirect",
    'E大发车合集': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2467166481575985152&scene=173&from_msgid=2653411345&from_itemidx=1&count=3&nolastread=1#wechat_redirect",
    '孟岩投资实证2022合集': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIzNTQ4ODg4OA==&action=getalbum&album_id=2206783352551063553&scene=173&from_msgid=2247487451&from_itemidx=1&count=3&nolastread=1#wechat_redirect",

}

# 下载所有合集
def down_all_album():
    output_dir_path = "D:\Media\Desktop\wechat2pdf"  # 指定主文件夹路径，不指定则为默认路径

    for album in album_url_dict.items():
        album_url = album[1]
        album_id = re.search(r'album_id=(\d+)&', album_url).group(1)  # 通过链接提取合集id
        # print(f'\nalbum_id：{album_id}\n')

        print(f"/n--------- 开始下载 {album[0]} ---------/n")
        wechat2pdf(album_url, output_dir_path)


# 仅下载最新的一篇文章
# 因为公众号每天只能发布一篇文章，所以只要运行一次 down_all_album，以后每天运行 down_new_post 即可保持文章同步更新
# def down_new_post():



if __name__ == "__main__":
    start_time = time.time()

    # 开始下载
    down_all_album()

    end_time = time.time()
    all_time = int(end_time - start_time)
    # print(f"\n本次共生成 {msg_num} 篇文章！")
    print(f"/n总耗时：{all_time}秒")

    print("/nDone!")
