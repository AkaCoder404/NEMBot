# NEMBot : NetEase Music Bot 

NEMBot是一个非常简单的网易音乐的API。提供网易云音乐 Python3 组件库. 
It is a library for parsing Netease Cloud Music to retrieve personal account information as well as publically availible information such as music, playlists, and more. 

基本上是ncmbot, https://github.com/xiyouMc/ncmbot的更新，因为它只支持Python 2. 这版本可以用Python3!

## 如何装使 然后 简单使用

1. clone this repository
2. pip install -r requirements.txt
3. import NEMBot

登录

```python
import NEMBot

bot = NEMBot()
login = bot.login(username="username", password="password")
print(login)
```

获取用户歌单列表

```python
user_playlists = bot.user_playlist(uid="user_id")
for playlist in user_playlists:
	print(playlist["id"], playlist["name"], playlist["trackCount"])
```

## 功能
1. 登录、推出功能 
2. 获取私人FM, 私人FM点赞，Dislike，每日签到
3. 用户歌单，关注列表，粉丝列表，用户动态，播放历史列表
4. 获取精品歌单，特色榜歌单
5. 搜索功能
6. 获取歌单的所有音乐
7. 获取热门歌手，歌手信息，歌手专辑
8. 获取专辑内容，评论
9. 获取歌曲评论，内容，和歌词
等等

## In Progress (maybe)
1. 全球媒体榜下载
2. 评论点赞
3. 下载音乐功能
4. 做成pip能下载的库，目前只能从github下载

## Thanks
大部分代码是按这些题库做出来的
1. https://github.com/xiyouMc/ncmbot 
2. https://github.com/topics/netease-musicbox
