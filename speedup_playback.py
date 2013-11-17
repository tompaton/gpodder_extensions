# -*- coding: utf-8 -*-
# This extension adjusts the playback speed of audio files
# Supported file formats are mp3
#
# Requires: sox
#
# Based on audio_converter.py
# https://github.com/gpodder/gpodder/blob/master/share/gpodder/extensions/audio_converter.py
#
# (c) 2013-11-16 Tom Paton <tom.paton@gmail.com>
# Released under the same license terms as gPodder itself.

import os
import subprocess

import gpodder
from gpodder import util

import logging
logger = logging.getLogger(__name__)

_ = gpodder.gettext

__title__ = _('Speed up audio playback with re-encoding')
__description__ = _('Increase the playback speed of audio files with sox')
__authors__ = 'Tom Paton <tom.paton@gmail.com>'
__doc__ = ''
__payment__ = ''
__category__ = 'post-download'

DefaultConfig = {
    'context_menu': True,  # Show action in the episode list context menu
    'speed': 1.33,  # playback speed factor
    'mono': False,  # convert to 64kbit mono 22khz too
}

class gPodderExtension:
    MIME_TYPES = ('audio/mpeg', )
    EXT = ('.mp3', )
    CMD = {'sox': {'.mp3': ['--multi-threaded',
                            '--buffer', '32768',
                            '--norm',
                            '%(old_file)s', '%(new_file)s',
                            'tempo', '-s', '%(speed).2f'],
                   '.mp3-mono': ['channels', '1', 'rate', '22050'],
               },
       }

    def __init__(self, container):
        self.container = container
        self.config = self.container.config

        # Dependency checks
        self.command = self.container.require_any_command(['sox',])

        # extract command without extension (.exe on Windows) from command-string
        self.command_without_ext = os.path.basename(os.path.splitext(self.command)[0])

    def on_episode_downloaded(self, episode):
        self._convert_episode(episode)

    def _check_source(self, episode):
        if not episode.file_exists():
            return False

        if '.fast.' in episode.local_filename(create=False):
            return False

        if episode.mime_type in self.MIME_TYPES:
            return True

        if episode.extension() in self.EXT:
            return True

        return False

    def on_episodes_context_menu(self, episodes):
        if not self.config.context_menu:
            return None

        if not any(self._check_source(episode) for episode in episodes):
            return None

        menu_item = _('Speed-up playback by %(speed).2fx') % {'speed': self.config.speed}

        return [(menu_item, self._convert_episodes)]

    def _convert_episode(self, episode):
        if not self._check_source(episode):
            return

        old_filename = episode.local_filename(create=False)
        filename, old_extension = os.path.splitext(old_filename)
        new_filename = filename + '.fast' + old_extension

        cmd_param = self.CMD[self.command_without_ext][old_extension]
        if self.config.mono:
            cmd_param.extend(self.CMD[self.command_without_ext][old_extension+'-mono'])
        cmd = ['nice', self.command] \
              + [param % {'old_file': old_filename,
                          'new_file': new_filename,
                          'speed': self.config.speed}
                 for param in cmd_param]

        sox = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdout, stderr = sox.communicate()

        if sox.returncode == 0:
            util.rename_episode_file(episode, new_filename)
            os.remove(old_filename)

            logger.info('File re-encoded at %(speed).2fx speed.' % {'speed': self.config.speed})
            gpodder.user_extensions.on_notification_show(_('File converted'), episode.title)
        else:
            logger.warn('sox failed: %s / %s', stdout, stderr)
            gpodder.user_extensions.on_notification_show(_('Speed-up failed'), episode.title)

    def _convert_episodes(self, episodes):
        for episode in episodes:
            if episode.was_downloaded(and_exists=True):
                self._convert_episode(episode)
