import sys
import time
import argparse 
import random
import urllib

import png
import requests
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



def decode_png_pixel_row(row, w, plane_count, alpha, palette):
	for i in range(w):
		pixel_data = row[plane_count * i:plane_count * (i + 1)]
		if alpha and pixel_data[-1] != 255:
			yield None
		else:
			yield get_closest_color_from_palette(tuple(pixel_data[:-1]), palette)



def load_image_from_png(png_reader, palette):
	# Load the image data
	w, h, pixels, metadata = png_reader.read()

	# Interpret the image metadata
	plane_count, alpha = metadata['planes'], metadata['alpha']

	# Decode the data
	img = tuple(tuple(col for col in decode_png_pixel_row(row, w, plane_count, alpha, palette)) for i, row in enumerate(pixels))

	# Job done	
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


	
def search_non_transparent_pixel(img, w, h):
	while True:
		x, y = random.randint(0, w - 1), random.randint(0, h - 1)
		if img[y][x] is not None:
			return x, y



def search_pixel_to_modify(session, img, w, h, xoffset, yoffset):
	while True:
		x, y = search_non_transparent_pixel(img, w, h)
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
	cmd_parser.add_argument('img_url',
	                        help = 'URL or path to the picture to reproduce')
	args = cmd_parser.parse_args()
	
	# Load the input image
	try:
		img_file = urllib.urlopen(args.img_url)
		img, w, h = load_image_from_png(png.Reader(file = img_file), fixed_palette)
	except IOError as e:
		sys.stderr.write('%s\n' % e)
		sys.exit(0)
	except png.FormatError as e:
		sys.stderr.write('Unable to load {}, wrong format\n'.format(args.img_url))
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
