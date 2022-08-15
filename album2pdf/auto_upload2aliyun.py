# !python
# auto_upload2aliyun.py - 自动将新增文件上传至阿里云盘

# 暂时每次有新文章时所有文件夹都同步一遍，后面再优化为单独同步，
# 主要为了减少 get_folder_by_path() 运行次数
# 更好的方法是，第一次运行 get_folder_by_path() 后取得 file_id, 以后就不用再去获取了


from aligo import Aligo


if __name__ == '__main__':

    ali = Aligo()  # 第一次使用，会弹出二维码，供扫描登录

    # 比如云盘目录为 /我的资源/1080p， 打头的 / 可加可不加
    remote_folder1 = ali.get_folder_by_path('/公众号&微博文章/E大公号/日记')
    remote_folder2 = ali.get_folder_by_path('/公众号&微博文章/E大公号/长赢指数投资计划')
    remote_folder3 = ali.get_folder_by_path('/公众号&微博文章/孟岩公号/孟岩投资实证（2022）')
    print(remote_folder1.file_id + '\n' + remote_folder2.file_id+ '\n' + remote_folder3.file_id)
    

    # 同步文件夹，本地为主
    # ali.sync_folder('D:\\Media\\Desktop\\wechat2pdf\\日记', remote_folder1.file_id, True)
    # ali.sync_folder('D:\\Media\\Desktop\\wechat2pdf\\长赢指数投资计划', remote_folder2.file_id, True)
    # ali.sync_folder('D:\\Media\\Desktop\\wechat2pdf\\孟岩投资实证（2022）', remote_folder3.file_id, True)


    
    # ali.upload_file("D:\\Media\\Desktop\\wechat2pdf\\长赢指数投资计划\\2.2022年8月ETF计划（一）：S买入一份；进一步理清那件事的思路-2022-08-03(img).pdf", remote_folder1.file_id)
    # ali.upload_folder('D:/迅雷下载', parent_file_id=remote_folder.file_id)
    