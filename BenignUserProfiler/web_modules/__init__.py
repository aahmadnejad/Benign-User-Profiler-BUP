#!/usr/bin/env python3

from .base_browser import BaseBrowserModule
from .soundcloud import SoundcloudModule
from .image_download import ImageDownloadModule
from .youtube import YoutubeModule
from .web_browse import WebBrowseModule

def get_module(module_type, headless=False):
    modules = {
        "soundcloud": SoundcloudModule,
        "download": ImageDownloadModule,
        "youtube": YoutubeModule,
        "web": WebBrowseModule
    }
    
    if module_type.lower() in modules:
        return modules[module_type.lower()](headless=headless)
    return WebBrowseModule(headless=headless)