import re;

macroTagRegex = r'\w[\w\-_]+'
valueRegex = r'\w+'

macroRegex = ''.join([
	# Tag itself
	r'(?P<tag>', macroTagRegex, r')', r'\s*',
	# 'Physical' start parenthesis
	r'\(', r'\s*',
	# Argument group (optional)
	r'(?P<arguments>',
		# First argument
		valueRegex, r'\s*',
		# The rest
		r'(,', r'\s*', valueRegex, r'\s*', r')*',
	r')?',
	# 'Physical' end parenthesis
	r'\s*', r'\)'
]);

while True:
	l = input('>> ');
	if l == '':
		break;

	result = re.search(macroRegex, l);
	if result:
		print('true');
		print(result.group("tag"));
		if result.group("arguments"):
			print([arg.strip() for arg in result.group("arguments").split(',')]);
	else:
		print('false');
