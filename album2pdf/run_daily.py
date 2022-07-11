#! python
# run_daily.py - 每天遍历合集列表，然后自动下载最新文章

import re
from album2pdf_v1 import wechat2pdf

# 自己感兴趣的合集链接
album_url_dict = {
    'E大日记合集': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2461687967875416065&scene=173&from_msgid=2653411356&from_itemidx=1&count=3&nolastread=1#wechat_redirect",
    'E大发车合集': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2467166481575985152&scene=173&from_msgid=2653411345&from_itemidx=1&count=3&nolastread=1#wechat_redirect",
    '孟岩投资实证2022合集': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIzNTQ4ODg4OA==&action=getalbum&album_id=2206783352551063553&scene=173&from_msgid=2247487451&from_itemidx=1&count=3&nolastread=1#wechat_redirect",

}

def down_all_album():
    output_dir_path = "D:\Media\Desktop\wechat2pdf2"  # 指定主文件夹路径，不指定则为默认路径

    for album in album_url_dict.items():
        album_url = album[1]
        album_id = re.search(r'album_id=(\d+)&', album_url).group(1)  # 通过链接提取合集id
        # print(f'\nalbum_id：{album_id}\n')

        print(f"--------- 开始下载 {album[0]} ---------")
        wechat2pdf(album_url, output_dir_path)


if __name__ == "__main__":
    down_all_album()
