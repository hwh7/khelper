#!/usr/bin/python

from sys import argv
from subprocess import Popen, PIPE
from os import listdir
from urllib2 import urlopen
from StringIO import StringIO
from time import time

def print_usage(argv):
	print 'Khelper for kernel development'
	print 'Usage: %s [COMMAND] [ARGUMENTS]' % argv[0]
	print 'test_sendemail [PATCH_FILES]: send patch files only to me'
	print 'mapply [STARTING PATCH_FILE_NUMBER] [END PATCH_FILE_NUMBER]: apply multiple patch files which are prefixed by the number'
	print 'mapply_patchwork [URL_FOR_PATCHWORK_PATCH_LIST] [FIRST PATCH ID] [# OF SUCCESSIVE PATCHES]: apply multiple patches which are found in patchwork'
	print 'apply_patchwork [PATCH ID]: apply the patch which is found in patchwork'

def get_usermail():
	p = Popen(['git', 'config', 'user.email'], stdout=PIPE)
	output = p.communicate()
	return output

def test_sendemail(argv):
	email = get_usermail()[0][0:-1]

	for i in range(2, len(argv)):
		Popen(['git', 'send-email', '--suppress-cc', 'all', '--to', email,  argv[i]]).communicate()

def mapply(argv):
	files = listdir('.')

	i = int(argv[2])
	end = int(argv[3])
	for file in files:
		if file.endswith('patch'):
			if file.startswith('%.04d' % i):
				p = Popen(['git', 'am', file])
				output = p.communicate()
				i += 1

		if i > end:
			break

def get_patchname(filename):
	f = open(filename)
	lines = f.readlines()

	title = ''
	for i in range(0, len(lines)):
		line = lines[i]
		if line.startswith('Subject'):
			if line[9] == '[':
				if ']' not in line:
					while ']' not in line:
						title += line[:-1]
						i += 1
						line = lines[i]
				idx = line.index(']')
				title += line[idx+2:-1]
			else:
				title += line[9:-1]
			title += ' '
			i += 1
			line = lines[i]
			if not line.startswith('From'):
				title += line[1:-1]
			return title

def convert_to_filename(patchname, idx):
	replaced_chars = ['/', ':', ' ', '\'', '\"']

	replaced = False
	to_be_filename = '%.04d-' % idx
	for char in patchname:
		if char in replaced_chars:
			if replaced:
				continue
			replaced = True
			char = '-'
		else:
			replaced = False

		to_be_filename += char

	return to_be_filename[:57] + '.patch'

def apply_patchwork_id(id, idx):
	filename = 'patch-%s-%f.patch' % (id, time())
	p = Popen(['wget', '-q', '-O', filename , 'https://patchwork.kernel.org/patch/%s/mbox/' % id]).communicate()
	patchname = get_patchname(filename)
	to_be_filename = convert_to_filename(patchname, idx)
	Popen(['mv', filename , to_be_filename])
	Popen(['git', 'am', to_be_filename]).communicate()

def apply_patchwork(argv):
	id = argv[2]
	apply_patchwork_id(id, 0)

def mapply_patchwork(argv):
	url = argv[2]
	start_id = argv[3]
	len = int(argv[4])

	ids = []
	lines = StringIO(urlopen(url).read())
	for line in lines:
		if 'patch_row' in line:
			ids.append(line[20:27])

	ids.reverse()

	i = 1
	get_download = False
	for id in ids:
		if i < len+1 and (get_download or start_id == id):
			apply_patchwork_id(id, i)
			get_download = True
			i += 1

funcs = {
	'test_send-email': test_sendemail,
	'te': test_sendemail,
	'mapply': mapply,
	'ma': mapply,
	'mapply_patchwork': mapply_patchwork,
	'mp': mapply_patchwork,
	'apply_patchwork': apply_patchwork,
	'ap': apply_patchwork,
}

def main():
	if len(argv) < 2:
		print_usage(argv)
		exit(0)

	funcs[argv[1]](argv)

if __name__ == "__main__":
	main()
