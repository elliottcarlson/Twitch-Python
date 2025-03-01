from typing import Dict, Any

import twitch.helix as helix
import twitch.v5 as v5
from twitch.api import API
from .model import Model


class Clip(Model):

    def __init__(self, api: API, data: Dict[str, Any]):
        super().__init__(api, data)

        self.id: str = data.get('id')
        self.url: str = data.get('url')
        self.embed_url: str = data.get('embed_url')
        self.broadcaster_id: str = data.get('broadcaster_id')
        self.broadcaster_name: str = data.get('broadcaster_name')
        self.creator_id: str = data.get('creator_id')
        self.creator_name: str = data.get('creator_name')
        self.video_id: str = data.get('video_id')
        self.game_id: str = data.get('game_id')
        self.language: str = data.get('language')
        self.title: str = data.get('title')
        self.view_count: int = data.get('view_count')
        self.created_at: str = data.get('created_at')
        self.thumbnail_url: str = data.get('thumbnail_url')
        self.duration: str = data.get('duration')

    def __str__(self):
        return self.title

    @property
    def user(self) -> 'helix.User':
        return helix.Users(self._api, int(self.broadcaster_id))[0]
