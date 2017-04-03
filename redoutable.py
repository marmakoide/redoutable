import sys
import time
import argparse 
import random

import requests
from PIL import Image
from requests.adapters import HTTPAdapter




# --- Color conversion to r/place' fixed color palette ------------------------

fixed_palette = [
	(255, 255, 255),
	(228, 228, 228),
	(136, 136, 136),
	( 34,  34,  34),
	(255, 167, 209),
	(229,   0,   0),
	(229, 149,   0),
	(160, 106,  66),
	(229, 217,   0),
	(148, 224,  68),
	(  2, 190,   1),
	(  0, 211, 211),
	(  0, 131, 199),
	(  0,   0, 234),
	(207, 110, 228),
	(130,   0, 128)
]



def color_dist(u, v):
	return sum((x - y) ** 2 for x, y in zip(u, v))



def get_closest_color_from_palette(u, palette):
	return min((color_dist(u, v), i) for i, v in enumerate(palette))[1]



def convert_for_palette(img, palette):
	w, h = img.width, img.height
	img = tuple(tuple(get_closest_color_from_palette(img.getpixel((j, i)), palette) for j in range(w)) for i in range(h))
	return img, w, h



# --- API for Reddit r/place --------------------------------------------------

def get_session(user, password):
	session = requests.Session()
	session.mount('https://www.reddit.com', HTTPAdapter(max_retries = 5))
	session.headers['User-Agent'] = 'redoutable.py'
	ret = session.post('https://www.reddit.com/api/login/{}'.format(user),
	data = {
		'user'     : user,
		'passwd'   : password,
		'api_type' : 'json'
	}).json()['json']
	
	if len(ret['errors']) > 0:
		sys.stdout.write(ret['errors'][0][1] + '\n')
		sys.exit(0)

	session.headers['x-modhash'] = ret['data']['modhash']
	return session



def read_pixel(session, x, y):
	while True:
		ret = session.get('http://reddit.com/api/place/pixel.json?x={}&y={}'.format(x, y), timeout = 5)
		if ret.status_code == 200:
			return ret.json()['color']


	
def search_pixel_to_modify(session, img, w, h, xoffset, yoffset):
	while True:
		x, y = random.randint(0, w - 1), random.randint(0, h - 1)
		if img[y][x] != read_pixel(session, x + xoffset, y + yoffset):
			return x, y
		time.sleep(5)



def write_pixel(session, x, y, col):
	ret = session.post('https://www.reddit.com/api/place/draw.json',
	                   data = { 'x': str(x), 'y' : str(y), 'color': str(col) }).json()
	if 'error' in ret:
		return float(ret['wait_seconds'])
	else:
		return None



# --- Entry point -------------------------------------------------------------

def main():
	# Command line parsing
	cmd_parser = argparse.ArgumentParser(description = "Script to automate r/place collaboration")
	cmd_parser.add_argument('-u', '--user', required =  True,
	                        help = 'username')
	cmd_parser.add_argument('-p', '--password', required = True,
	                        help = 'password')
	cmd_parser.add_argument('-x', '--xoffset', type = int, default = 0,
	                        help = 'x position of upper-left corner image')
	cmd_parser.add_argument('-y', '--yoffset', type = int, default = 0,
	                        help = 'y position of upper-left corner image')
	cmd_parser.add_argument('img_path',
	                        help = 'Path to the picture to reproduce')
	args = cmd_parser.parse_args()
	
	# Read the input image
	try:
		img, w, h = convert_for_palette(Image.open(args.img_path), fixed_palette)
	except IOError as e:
		sys.stderr.write('%s\n' % e)
		sys.exit(0)

	# Connect to Reddit
	session = get_session(args.user, args.password)

	# Modify pixels
	while True:
		# Select a pixel to modify
		u, v = search_pixel_to_modify(session, img, w, h, args.xoffset, args.yoffset)
		x, y = u + args.xoffset, v + args.yoffset
 
		# Try to modify it
		t = write_pixel(session, x, y, img[v][u])
		if t > 0:
			sys.stdout.write('Sleep for {} seconds\n'.format(t))
			time.sleep(t + 2)
		else:
			sys.stdout.write('Wrote pixel {}x{}\n'.format(x, y))



if __name__ == '__main__':
	main()
