from decimal import Decimal
from datetime import timedelta
from datetime import datetime


def duration_string(string):  # I hate regex even though I should be using it here
	string = string.lower()
	if 'd' not in string and 'h' not in string and 'm' not in string and 's' not in string:
		raise ValueError(
			'There were no duration multiplyer characters ("d", "h", "m", or "s") provided in "{}"'.format(string)
		)
	total_seconds = Decimal('0')
	prev_num = []
	for character in string:
		if character.isalpha():
			if prev_num:
				num = Decimal(''.join(prev_num))
				if character == 'd':
					total_seconds += num * 60 * 60 * 24
				elif character == 'h':
					total_seconds += num * 60 * 60
				elif character == 'm':
					total_seconds += num * 60
				elif character == 's':
					if num == int(num):
						total_seconds += num
					else:
						raise ValueError('Seconds ({}) must be a whole number'.format(num))
				prev_num = []
		elif character.isnumeric() or character == '.':
			prev_num.append(character)
	return timedelta(seconds=int(total_seconds))


def datetime_string(string, custom_format=None):
	try:
		# noinspection PyUnresolvedReferences
		from dateutil.parser import parser
		return parser().parse(string)
	except ImportError:
		string = string.replace('/', '-')
		formats = [
			'%Y',
			'%Y-%m',
			'%Y-%m-%d',
			'%Y-%m-%d %H',
			'%Y-%m-%d %H:%M',
			'%Y-%m-%d %H:%M:%S',
			'%Y-%m-%d %I:%M:%S %p'
		]
		if custom_format:
			formats.insert(0, custom_format)
		for f in formats:
			try:
				return datetime.strptime(string, f)
			except ValueError:
				continue
		raise ValueError('The string did not match any configured format')
