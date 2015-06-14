#!/usr/bin/python

from sys import argv
from subprocess import Popen, PIPE

def print_usage(argv):
	print 'Khelper for kernel development'
	print 'Usage: %s [COMMAND] [ARGUMENTS]' % argv[0]
	print 'test_sendemail [PATCH_FILES]: send patch files only to me'

def get_usermail():
	p = Popen(['git', 'config', 'user.email'], stdout=PIPE)
	output = p.communicate()
	return output

def test_sendemail(argv):
	email = get_usermail()[0][0:-1]

	for i in range(2, len(argv)):
		Popen(['git', 'send-email', '--suppress-cc', 'all', '--to', email,  argv[i]]).communicate()

funcs = {
	'test_send-email': test_sendemail,
}

def main():
	if len(argv) < 2:
		print_usage(argv)
		exit(0)

	funcs[argv[1]](argv)

if __name__ == "__main__":
	main()
