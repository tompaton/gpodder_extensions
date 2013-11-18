gpodder_extensions
==================

Custom extensions for gPodder podcast client

See http://gpodder.org/, place .py files in ~/gPodder/Extensions (create if necessary) and restart gPodder.

For other extensions, have a look at http://wiki.gpodder.org/wiki/Extensions


speedup_playback.py
-------------------

This will re-encode an mp3 file at a faster speed without increasing the pitch and
making it sound like a chipmunk. How this actually works is pretty neat:
http://www.surina.net/article/time-and-pitch-scaling.html

Additionally it will normalizes the audio to prevent clipping and optionally drop the quality down
to mono 22.1kHz which works better for me when listening while riding my bike or running.

Requires: http://sox.sourceforge.net/sox.html
