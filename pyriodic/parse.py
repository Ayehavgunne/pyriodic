from decimal import Decimal
from datetime import timedelta
from datetime import datetime as dt

def duration(duration_string):#I hate regex even though I should be using it here
	duration_string = duration_string.lower()
	total_seconds = Decimal('0')
	prev_num = []
	for character in duration_string:
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
						raise ValueError('Seconds ({}) must be represented as an interger'.format(num))
				prev_num = []
		elif character.isnumeric() or character == '.':
			prev_num.append(character)
	return timedelta(seconds=int(total_seconds))

def datetime(datetime_string):
	try:
		# noinspection PyUnresolvedReferences
		from dateutil.parser import parser
		return parser().parse(datetime_string)
	except ImportError:
		if '-' in datetime_string and ':' in datetime_string:
			return dt.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
		elif '/' in datetime_string and ':' in datetime_string:
			return dt.strptime(datetime_string, '%Y/%m/%d %H:%M:%S')
		elif '-' in datetime_string:
			return dt.strptime(datetime_string, '%Y-%m-%d')
		elif '/' in datetime_string:
			return dt.strptime(datetime_string, '%Y/%m/%d')
		elif ':' in datetime_string:
			return dt.strptime(datetime_string, '%H:%M:%S')