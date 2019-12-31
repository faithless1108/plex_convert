#!/usr/bin/env python
from pprint import pprint
from plexapi.server import PlexServer
import ntpath
import subprocess
import shutil
import logging
import os

ep2conv = list()
outputbase = '/export/Downloads/'
profile_path = '/root/'
logfile = outputbase + 'convert_log.log'

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}



baseurl = 'http://localhost:32400'
token = 'xxxxxxx_xxxxxxx'
plex = PlexServer(baseurl, token)

FORMAT = '%(asctime)-15s  %(message)s'
#logging.basicConfig(format=FORMAT)
formatter = logging.Formatter(FORMAT)

log = logging.getLogger('LOG')
log.setLevel(logging.INFO)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
             logfile, maxBytes=20000000, backupCount=5)

handler.setFormatter(formatter)

log.addHandler(handler)


shows = plex.library.section('TV-Serien')
for show in shows.search():
	for episode in show.episodes():   
		for media in episode.media:
			if  media.videoCodec != 'hevc':
				for parts in media.parts:
					input_file = parts.file
					output_file = ntpath.basename(input_file)
					ep2conv.append([input_file,outputbase+output_file,media.videoResolution,episode.type,parts.size])


for item in ep2conv:
	if item[2] != '720' and item[2] != '1080':
		continue

	input_file = item[0]
	output_file = item[1]
	profile = item[3]+"_"+item[2]
	profile_f = profile_path + profile+".json"
	size_old = (item[4] / (1024 * 1024))

	cmd = "nice -n 19 handbrake-cli -i \"%s\"  -o \"%s\" --preset-import-file %s -Z %s " % (input_file, output_file, profile_f, profile)
	log.info("Begin processing %s -> Size: %d" %(input_file,size_old))
	p = subprocess.call(cmd, shell=True)
	if p == 0:
		file_stats = os.stat(output_file)
		size_new = file_stats.st_size / (1024 * 1024)
		shutil.move(output_file, input_file)
		per_saved = round((1 - (size_new / size_old)) *100)
		log.info("Finished  processing %s -> Size: %d ->  Saved: %d"  %(input_file, size_new, per_saved))
	else:
		log.error("Somthing went wrong during conversion")

