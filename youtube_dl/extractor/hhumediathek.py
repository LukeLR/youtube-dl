# coding: utf-8
from __future__ import unicode_literals
import json, re

from .common import InfoExtractor
from ..utils import js_to_json


class HHUMediathekIE(InfoExtractor):
    _VALID_URL = r'https?://mediathek\.hhu\.de/watch/(?P<id>[0-9a-e]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    _TEST = {
        'url': 'https://mediathek.hhu.de/watch/7db1e695-b4c2-46a7-9227-1b22d7c7c05f',
        'md5': '7a6ab682c8c010c688e74b2c0dedf0e3',
        'info_dict': {
            'id': '7db1e695-b4c2-46a7-9227-1b22d7c7c05f',
            'ext': 'mp4',
            'title': 'Reinforcement Learning: Introduction + Bandits 2020',
            'creator': 'Prof. Dr. Stefan Harmeling',
            'uploader': 'harmeling',
            'uploader_url': 'https://mediathek.hhu.de/user/harmeling',
            'description': '',
            #'thumbnail': r're:^https?://.*\.jpg$',
            # TODO more properties, either as:
            # * A value
            # * MD5 checksum; start the string with md5:
            # * A regular expression; start the string with re:
            # * Any Python type (for example int or float)
        }
    }

    def _real_extract(self, url):
        base_url = "https://mediathek.hhu.de"
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        
        #jwplayer = self._extract_jwplayer_data(webpage, video_id)
        #print(jwplayer)
        #regex = re.compile(
        #    r'(?s)jwplayer\((?P<quote>[\'"])[^\'" ]+(?P=quote)\)(?!</script>).*?\.setup\s*\((?P<options>[^;]+)\;')
        #print(regex.findall(webpage))
        #jwplayer_data = self._parse_json(mobj.group('options'),
        #                                         video_id=video_id,
        #                                         transform_source=True)

        # TODO more code goes here, for example ...
        title = self._html_search_regex(r'<h1 id="mt_watch-headline-title">\s*<span title=".*" dir="ltr">(.+?)</span>', webpage, 'title')
        print(title)
        creator = self._html_search_regex(r'<div id="mt_watch-headline-additional-information" class="watch-headline-additional-information">\s*<span title=".+">(.+?)</span>', webpage, 'creator')
        print(creator)
        uploader = self._html_search_regex(r'<a id="mt_content_placeholder_videoinfo_createdby" class="author" href=".+">(.+?)</a>', webpage, 'uploader')
        print(uploader)
        uploader_url = base_url + self._html_search_regex(r'<a id="mt_content_placeholder_videoinfo_createdby" class="author" href="(.+?)">', webpage, 'uploader_url')
        print(uploader_url)
        try:
            description = self._html_search_regex(r'<p id="mt_watch-description" class="watch-description">\s*([^\s].+[^\s]?)\s*</p>', webpage, 'description')
        except:
            description = ""
        print(description)
        sources = self._search_regex(r'(?s)sources: (\[[^\]]*\])', webpage, 'sources')
        sources = js_to_json(sources)
        sources_array = json.loads(sources)
        
        formats = []
        
        height_regex = re.compile(r'([0-9]+)p')
        ext_regex = re.compile(r'\.(.+)$')
        for source in sources_array:
            print(source)
            height = int(height_regex.search(source['label']).groups()[0])
            extension = ext_regex.search(source['file']).groups()[0]
            
            formats.append({'url': base_url + source['file'], 'ext': extension, 'height': height})
        
        def comparator(x, y):
            format_metric = lambda x: 1 if x == 'mp4' else 0
            x['format_metric'] = format_metric(x['ext'])
            y['format_metric'] = format_metric(y['ext'])
            
            return (x['height'] - y['height']) * 10 + x['format_metric'] - y['format_metric']
        
        def cmp_to_key(mycmp):
            'Convert a cmp= function into a key= function'
            class K:
                def __init__(self, obj, *args):
                    self.obj = obj
                def __lt__(self, other):
                    return mycmp(self.obj, other.obj) < 0
                def __gt__(self, other):
                    return mycmp(self.obj, other.obj) > 0
                def __eq__(self, other):
                    return mycmp(self.obj, other.obj) == 0
                def __le__(self, other):
                    return mycmp(self.obj, other.obj) <= 0
                def __ge__(self, other):
                    return mycmp(self.obj, other.obj) >= 0
                def __ne__(self, other):
                    return mycmp(self.obj, other.obj) != 0
            return K
        
        formats.sort(key=cmp_to_key(comparator))

        return {
            'id': video_id,
            'title': title,
            'creator': creator,
            'uploader': uploader,
            'uploader_url': uploader_url,
            'description': description,
            'formats': formats
            # TODO more properties (see youtube_dl/extractor/common.py)
        }
