#!/usr/bin/python

from sys import argv

def print_usage():
	print "print_usage"

funcs = {
}

def main():
	if len(argv) < 2:
		print_usage()
		exit(0)

	funcs[argv[1]](argv)

if __name__ == "__main__":
	main()
