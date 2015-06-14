#!/usr/bin/python

from sys import argv
from subprocess import Popen, PIPE
from os import listdir

def print_usage(argv):
	print 'Khelper for kernel development'
	print 'Usage: %s [COMMAND] [ARGUMENTS]' % argv[0]
	print 'test_sendemail [PATCH_FILES]: send patch files only to me'
	print 'mapply [STARTING PATCH_FILE_NUMBER] [END PATCH_FILE_NUMBER]: apply multiple patch files which are prefixed by the number'

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

funcs = {
	'test_send-email': test_sendemail,
	'mapply': mapply,
}

def main():
	if len(argv) < 2:
		print_usage(argv)
		exit(0)

	funcs[argv[1]](argv)

if __name__ == "__main__":
	main()
