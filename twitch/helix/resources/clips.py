from typing import List, Union, Tuple, Generator

import twitch.helix as helix
import twitch.v5 as v5
from twitch.api import API
from .resource import Resource


class Clips(Resource['helix.Clip']):
    DEFAULT_FIRST: int = 20
    FIRST_API_LIMIT: int = 100
    ID_API_LIMIT: int = 100
    CACHE_PREFIX: str = 'helix.clip.'

    def __init__(self,
		 api: API,
		 clip_ids: Union[int, List[int]] = None,
		 **kwargs):
	super().__init__(api=api, path='clips')

	# Store kwargs as class property for __iter__
	self._kwargs = kwargs

	# 'id' parameter can be a singular or a list
	# Create list of clip ids by combining clip_ids and kwargs['id']

	# Convert singular string to list
	if 'id' in self._kwargs and type(self._kwargs['id']) == str:
	    self._kwargs['id'] = [self._kwargs['id']]

	self._kwargs['id'] = list(self._kwargs['id']) if 'id' in self._kwargs.keys() else []
	self._kwargs['id'] = self._kwargs['id'] + list(clip_ids) if clip_ids else self._kwargs['id']

	# Convert to integers
	self._kwargs['id'] = [int(x) for x in self._kwargs['id']]

	# Remove duplicates
	self._kwargs['id'] = list(set(self._kwargs['id'])) if self._kwargs['id'] else []

	# Download clip ids
	if len(self._kwargs['id']) > 0:
	    self._download_clip_ids()

    def _can_paginate(self) -> bool:
	"""
	Kwargs must include user_id or game_id
	:return: If resource can paginate
	"""
	# todo: maybe raise VideosAPIException('A user_id or a game_id must be specified.')
	return len([key for key in self._kwargs.keys() if key in ['broadcaster_id', 'game_id']]) == 1

    def _cache_clips(self, clips: List['helix.Clip']) -> None:
	"""
	Custom clip cache
	Cache individual clips
	:param clips: Helix clips
	:return: None
	"""
	if self._api.use_cache:
	    for clip in clips:
		API.SHARED_CACHE.set(f'{Clips.CACHE_PREFIX}{clip.id}', clip.data)

    def _handle_pagination_response(self, response: dict) -> List['helix.Clip']:
	"""
	Custom handling for clip pagination
	:param response: API response data
	:return: Videos
	"""
	clips: List['helix.Clip'] = [helix.Clip(api=self._api, data=clip) for clip in response['data']]
	self._cache_clips(clips)

	return clips

    def _next_clips_page(self, ignore_cache: bool = False) -> List['helix.Clip']:
	"""
	Video pagination
	:param ignore_cache: Ignore API cache
	:return: Videos
	"""
	response: dict = self._next_page(ignore_cache=ignore_cache)

	return self._handle_pagination_response(response)

    def _cache_download(self, clip_ids: List[int]) -> List[int]:
	"""
	Fetch data from cache
	:param clip_ids: Lookup the clip ids
	:return: Cache hits (clip ids)
	"""
	cache_hits: list = []
	for clip_id in clip_ids:
	    cache_data: dict = API.SHARED_CACHE.get(f'{Clips.CACHE_PREFIX}{clip_id}')
	    if cache_data:
		self._data.append(helix.Clip(api=self._api, data=cache_data))
		cache_hits.append(clip_id)

	return cache_hits

    def _download_clip_ids(self) -> None:
	"""
	Download clips by list of clip IDs
	:return:
	"""
	# Custom cache lookup
	if self._api.use_cache:
	    cache_hits: List[int] = self._cache_download(self._kwargs['id'])

	    # Removed cached ids from kwargs
	    self._kwargs['id'] = [n for n in self._kwargs['id'] if n not in cache_hits]

	# Download uncached clips from API
	if len(self._kwargs['id']) > 0:

	    # When the number of IDs exceeds API limitations, divide into multiple requests
	    remaining_clip_ids: list = self._kwargs['id']

	    while remaining_clip_ids:
		self._kwargs['id'] = remaining_clip_ids[:Clips.ID_API_LIMIT]

		# Ignore default caching method, as we want to cache individual clips and not a collection of clips.
		clips: List[helix.Clip] = self._next_clips_page(ignore_cache=True)

		# Save clips
		self._data.extend(clips)

		# Update remaining clip ids
		remaining_clip_ids = [] if len(clips) < len(remaining_clip_ids) else remaining_clip_ids[
											Clips.ID_API_LIMIT:]
