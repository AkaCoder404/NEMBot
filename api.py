#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NEMBot 

"""

__title__ = 'NEMBot'
__version__ = '0.1.0'

# imports
import json
import platform
from collections import OrderedDict
from http.cookiejar import Cookie
from http.cookiejar import LWPCookieJar

import requests
import requests_cache

from .config import Config
from .const import Constant
from .encrypt import encrypted_request, md5
from .storage import Storage

requests_cache.install_cache(Constant.cache_path, expire_after=3600)

CATEGORIES = OrderedDict(
  [ 
    ("语种", ["华语", "欧美", "日语", "韩语", "粤语"]),
    ("风格", ["流行", "摇滚", "民谣", "电子", "舞曲", "说唱", "轻音乐", "爵士", "乡村", "R&B/Soul", "古典", "民族", "英伦", "金属", "朋克", "蓝调", "雷鬼", "世界音乐", "拉丁", "另类/独立", "New Age", "古风", "Bossa Nova" ]),
    ("场景", ["清晨", "夜晚", "学习", "工作", "午休", "下午茶", "地铁", "驾车", "运动", "旅行", "散步", "酒吧"]),
    ("情感", ["怀旧", "清新", "浪漫", "性感", "伤感", "治愈", "放松", "孤独", "感动", "兴奋", "快乐", "安静", "思念"]),
    ("主题", ["影视原声","ACG","儿童","校园","游戏","70后","80后","90后","网络歌曲","KTV","经典","翻唱","吉他","钢琴","器乐","榜单","00后"]),
  ]
)

# 云音乐特色榜
SPECIAL_CHART = {
  0 : ["云音乐飙升榜", "19723756"],
  1 : ["云音乐新歌榜", "3779629"],
  2 : ["云音乐原创榜", "2884035"],
  3 : ["云音乐热歌榜", "3778678"],
}

# 全球媒体榜
GLOBAL_CHART = {}

class NEMBot(object):
  """
    Carries out all the functionality of NCMBot Object.
    It carries out all functionality regarding NetEase music
  """
  HOST_URL = "http://music.163.com"
  DEFAULT_TIMEOUT = 10

  def __init__(self):
    # Header
    self.header = {
      "Accept": "*/*",
      "Accept-Encoding": "gzip,deflate,sdch",
      "Accept-Language": "zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4",
      "Connection": "keep-alive",
      "Content-Type": "application/x-www-form-urlencoded",
      "Host": "music.163.com",
      "Referer": "http://music.163.com",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.87 Safari/537.36",
    }

    # Storage and Cookie
    self.storage = Storage()
    cookie_jar = LWPCookieJar(self.storage.cookie_path)
    cookie_jar.load()
    self.session = requests.Session()
    self.session.cookies = cookie_jar
    for cookie in cookie_jar:
      if cookie.is_expired():
        cookie_jar.clear()
        self.storage.database["user"] = {
          "username": "",
          "password": "",
          "user_id": "",
          "nickname": "",
        }
        self.storage.save()
        break       

  def special_chart(self):
    return [item[0] for item in SPECIAL_CHART.values()]

  def global_chart(self):
    return [item[0] for item in GLOBAL_CHART.values()]

  def _raw_request(self, method, endpoint, data=None):
    resp = None
    if method == "GET":
      resp = self.session.get(endpoint, params=data, headers=self.header, timeout=self.DEFAULT_TIMEOUT)
    elif method == "POST":
      resp = self.session.post(endpoint, data=data, headers=self.header, timeout=self.DEFAULT_TIMEOUT)
    return resp
 
  # 生成Cookie对象
  def make_cookie(self, name, value):
    return Cookie(
      version=0,
      name=name,
      value=value,
      port=None,
      port_specified=False,
      domain="music.163.com",
      domain_specified=True,
      domain_initial_dot=False,
      path="/",
      path_specified=True,
      secure=False,
      expires=None,
      discard=False,
      comment=None,
      comment_url=None,
      rest={},
    )

  # 生成Request对象
  def request(self, method, path, params={}, default={"code": -1}, custom_cookies={}):
    endpoint = "{}{}".format(self.HOST_URL, path)
    csrf_token = ""
    for cookie in self.session.cookies:
      if cookie.name == "__csrf":
        csrf_token = cookie.value
        break
    params.update({"csrf_token": csrf_token})
    data = default

    for key, value in custom_cookies.items():
      cookie = self.make_cookie(key, value)
      self.session.cookies.set_cookie(cookie)

    params = encrypted_request(params)
    resp = None
    try:
      resp = self._raw_request(method, endpoint, params)
      data = resp.json()
    except requests.exceptions.RequestException as e:
      print(e)
    except ValueError:
      print("Path: {}, response: {}".format(path, resp.text[:200]))
    finally:
      return data

  # 登录
  def login(self, username, password):
    self.session.cookies.load()
    password = md5(password)
    if username.isdigit():
      path = "/weapi/login/cellphone"
      params = dict(
        phone=username,
        password=password,
        countrycode="86",
        rememberLogin="true",
      )
    else:
      path = "/weapi/login"
      params = dict(
        username=username,
        password=password,
        rememberLogin="true",
      )
    data = self.request("POST", path, params, custom_cookies={"os": "pc"})
    self.session.cookies.save()
    return data

  # 推出
  def logout(self):
    self.session.cookies.clear()
    self.storage.database["user"] = {
        "username": "",
        "password": "",
        "user_id": "",
        "nickname": "",
    }
    self.session.cookies.save()
    self.storage.save()

  # 获取用户信息
  def user_info(self):
    """"""
    return ""

  def personal_fm(self):
    """ 获取私人FM （需要登录）"""
    path = "/weapi/v1/radio/get"
    return self.request("POST", path).get("data", [])

  def fm_like(self, songid, like=True, time=25, alg="itembased"):
    """ 给FM 点赞（需要登录）
    :param songid: 通过歌曲id，给点赞
    """
    path = "/weapi/radio/like"
    params = dict(alg=alg, trackId=songid, like="true" if like else "false", time=time)
    return self.request("POST", path, params)["code"] == 200

  def fm_dislike(self, songid, time=25, alg="RT"):
    """ 给FM Dislike （需要登录）
    :param songid: 通过歌曲id，给Dislike
    """
    path = "/weapi/radio/trash/add"
    params = dict(songId=songid, alg=alg, time=time)
    return self.request("POST", path, params)["code"] == 200

  def daily_task(self, is_mobile=True):
    """ 每日签到 （需要登录）"""
    path = "/weapi/point/dailyTask"
    params = dict(type=0 if is_mobile else 1)
    return self.request("POST", path, params)

  def user_playlist(self, uid, offset=0, limit=30):
    """ 获取用户歌单 (不需要登录)
    :param uid: 通过用户ID，获取用户歌单
    :param offset: (optional) 分段起始位置，默认 0
    :param limit: (optional) 数据上限多少行，默认 50
    
    """
    path = "/weapi/user/playlist"
    params = dict(uid=uid, offset=offset, limit=limit)
    return self.request("POST", path, params).get("playlist", [])

  def user_follows(self, uid, offset="0", limit=30):
    """ 获取用户关注列表 （不需要登录）
    :param uid: 通过用户ID，获取用户关注列表
    :param offset: (optional) 分段起始位置，默认 0
    :param limit: (optional) 数据上限多少行，默认 30
    """
    path = "/weapi/user/getfollows/{}".format(uid)
    params = dict(uid=uid, offset=offset, limit=limit, order=True)
    return self.request("POST", path, params)

  def user_followers(self, uid, offset="0", limit=30):
    """ 获取用户粉丝 (不需要登录)
    :param uid: 通过用户ID，获取用户粉丝
    :param offset: (optional) 分段起始位置，默认 0
    :param limit: (optional) 数据上限多少行，默认 30
    """
    path = "/weapi/user/getfolloweds/{}".format(uid) 
    params = dict(uid=uid, offset=offset, limit=limit)
    return self.request("POST", path, params)

  def user_events(self, uid):
    """获取用户动态 (不需要登录)
    :param uid: 通过用户id，获取用户动态
    """
    path = "/weapi/event/get/{}".format(uid)
    params = dict(uid=uid)
    return self.request("POST", path, params)

  def user_record(self, uid, type=0):
    """ 获取用户播放记录 (不需要登录) 
    :param uid: 通过用户id，获取用户播放记录
    :param type: 所有记录（0）本周记录（1), 默认未0
    """
    path = "/weapi/v1/play/record"
    params = dict(uid=uid, type=type)
    return self.request("POST", path, params)

  def events(self):
    """ 获取各种动态，对应网页版网易云，朋友界面的各种动态消息，如分享的视频、音乐、照片等 (不需要登录)"""
    path = "/weapi/v1/event/get"
    params = {}
    return self.request("POST", path, params)

  def top_playlists_highquality(self, cat="全部", offset=0, limit=30):
    """获取精品歌单 (不需要登录)
    :param cat: (optional) 歌单类型，默认 ‘全部’
    :param offset: (optional) 分段起始位置，默认 0
    :param limit: (optional) 数据上限多少行，默认 30
    """

    path = "/weapi/playlist/highquality/list"
    params = dict(cat=cat, offset=offset, limit=limit)
    return self.request("POST", path, params).get("playlists", [])
  
  def daily_recommend_resource(self):
    """ 每日推荐歌单 (不需要登录)"""
    path = "/weapi/v1/discovery/recommend/resource"
    return self.request("POST", path).get("recommend", [])

  def daily_recommend_playlist(self, total=True, offset=0, limit=30):
    """ 每日推荐歌曲 （需要登录）
      :param offset: (optional) 分段起始位置，默认 0
      :param limit: (optional) 数据上限多少行，默认 20
    """
    
    path = "/weapi/v1/discovery/recommend/songs"
    params = dict(total=total, offset=offset, limit=limit)
    return self.request("POST", path, params).get("recommend", [])

  def top_songlist_special_chart(self, index=0):
    """ 获取特色榜单曲 （不需要登录）
    :param index: (optional), 通过SPECIAL的id获取特色榜单曲，默认0
    """
    playlist_id = SPECIAL_CHART[index][1]
    return self.playlist_songlist(playlist_id)

  def search(self, keywords, search_type=1, offset=0, total="true", limit=30):
    """ 搜索 （不需要登录）
    :param keywords: 通过用户输入的keywords，搜索不同type的内容
    :param type: (optional) 单曲(1)，歌手(100)，专辑(10)，歌单(1000)，用户(1002) *(type)*， 默认1
    :param offset: (optional) 分段起始位置，默认 0
    :param limit: (optional) 数据上限多少行，默认 30
    """
    path = "/weapi/search/get"
    params = dict(s=keywords, type=search_type, offset=offset, total=total, limit=limit)
    return self.request("POST", path, params).get("result", {})

  def new_albums(self, offset=0, limit=30):
    """ 获取新碟上架 (不需要登录)
    :param offset: (optional) 分段起始位置，默认 0
    :param limit: (optional) 数据上限多少行，默认 30
    """
    path = "/weapi/album/new"
    params = dict(area="ALL", offset=offset, total=True, limit=limit)
    return self.request("POST", path, params).get("albums", [])

  def top_playlists(self, cat="全部", order="hot", offset=0, limit=30):
    """ 获取歌单（网友精选碟）
    :param cat: (optional) 歌单类型，默认 ‘全部’
    :param offset: (optional) 分段起始位置，默认 0
    :param limit: (optional) 数据上限多少行，默认 30
    """
    path = "/weapi/playlist/list"
    params = dict(cat=cat, order=order, offset=offset, total="true", limit=limit)
    return self.request("POST", path, params).get("playlists", [])

  def playlist_catalogs(self):
    path = "/weapi/playlist/catalogue"
    return self.request("POST", path)

  def playlist_songlist(self, playlist_id):
    """ 获取对应歌单内的所有音乐的playlist id和trackIds （不需要登录）
    :param: 通过歌单id，获取歌单的所有音乐    
    """
    path = "/weapi/v3/playlist/detail"
    params = dict(id=playlist_id, total="true", limit=1000, n=1000, offest=0)
    # cookie添加os字段
    custom_cookies = dict(os=platform.system())
    return (self.request("POST", path, params, {"code": -1}, custom_cookies).get("playlist", {}).get("trackIds", []))

  def top_artists(self, offset=0, limit=30):
    """ 获取热门歌手 (不需要登录）
    :param offset: (optional) 分段起始位置，默认 0
    :param limit: (optional) 数据上限多少行，默认 30
    """
    path = "/weapi/artist/top"
    params = dict(offset=offset, total=True, limit=limit)
    return self.request("POST", path, params).get("artists", [])

  def artists(self, artist_id):
    """  获取歌手单曲 （不需要登录）
    :param artist_id: 通过歌手id，获取歌手单曲
    """
    path = "/weapi/v1/artist/{}".format(artist_id)
    return self.request("POST", path).get("hotSongs", [])

  def get_artist_album(self, artist_id, offset=0, limit=30):
    """  获取歌手专辑 （不需要登录）
    :param artist_id: 通过歌手id，获取歌手的所有专辑
    :param offset: (optional) 分段起始位置，默认 0
    :param limit: (optional) 数据上限多少行，默认 30
    """
    path = "/weapi/artist/albums/{}".format(artist_id)
    params = dict(offset=offset, total=True, limit=limit)
    return self.request("POST", path, params).get("hotAlbums", [])

  # 获取专辑内容 
  def album(self, album_id):
    path = "/weapi/v1/album/{}".format(album_id)
    return self.request("POST", path).get("songs", [])

  # 获取专辑所有评论
  def album_comments(self, album_id, offset=0, total="false", limit=100):
    path = "/weapi/v1/resource/comments/R_AL_4_{}/".format(album_id)
    params = dict(rid=album_id, offset=offset, total=total, limit=limit)
    return self.request("POST", path, params)

  # 获取该音乐的所有评论
  def song_comments(self, music_id, offset=0, total="false", limit=100):
    path = "/weapi/v1/resource/comments/R_SO_4_{}/".format(music_id)
    params = dict(rid=music_id, offset=offset, total=total, limit=limit)
    return self.request("POST", path, params)

  # 获取歌曲详情 
  def songs_detail(self, ids):
    path = "/weapi/v3/song/detail"
    params = dict(c=json.dumps([{"id": _id} for _id in ids]), ids=json.dumps(ids))
    return self.request("POST", path, params).get("songs", [])

  # 获取对应音乐的URL
  def songs_url(self, ids):
    quality = Config().get("music_quality")
    rate_map = {0: 320000, 1: 192000, 2: 128000}
    path = "/weapi/song/enhance/player/url/"
    params = dict(ids=ids, br=rate_map[quality])
    return self.request("POST", path, params).get("data", [])
  
  # 给品论点赞
  def like_comment(self, ids):
    path = "/weapi/v1/comment/{}".format(ids)
    params = dict()
    return self.request("POST", path, params)

  # 获取对应音乐的歌词
  def song_lyric(self, music_id):
    path = "/weapi/song/lyric"
    params = dict(os="osx", id=music_id, lv=-1, kv=-1, tv=-1)
    lyric = self.request("POST", path, params).get("lrc", {}).get("lyric", [])
    if not lyric:
      return []
    else:
      return lyric.split("\n")

  # 获取DJ的Channels
  def dj_channels(self, type=0, offset=0, limit=30):
    """ 
    :param type: (optional) 今日最热（0）, 本周最热（10），历史最热（20），最新节目（30），默认0
    :param offset: (optional) 分段起始位置，默认 0
    :param limit: (optional) 数据上限多少行，默认 30
    """
    path = "/weapi/djradio/hot/v1"
    params = dict(limit=limit, offset=offset)
    channels = self.request("POST", path, params).get("djRadios", [])
    return channels

  def dj_programs(self, radio_id, asc=False, offset=0, limit=50):
    path = "/weapi/dj/program/byradio"
    params = dict(asc=asc, radioId=radio_id, offset=offset, limit=limit)
    programs = self.request("POST", path, params).get("programs", [])
    return [p["mainSong"] for p in programs]

