#!/usr/bin/env python
import sys
import argparse

import resolwe_api


parser = argparse.ArgumentParser(description='POST a data object JSON.')

parser.add_argument('-a', '--address', default='http://cloud.genialis.com', help='Resolwe server address')
parser.add_argument('-e', '--email', default='anonymous@genialis.com', help='User e-mail')
parser.add_argument('-p', '--password', default='anonymous', help='User password')

args = parser.parse_args()


s = sys.stdin.read()
print s

re = resolwe_api.Resolwe(args.email, args.password, args.address)
re.create(s, 'data')
