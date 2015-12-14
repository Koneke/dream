import re;

# Sample macro
macroArgs = ['test'];
macroBody = 'span.foo#{test}: qux';

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

def feed(body, sig, args):
	result = body;
	for arg in args:
		source = arg;
		destination = '{' + sig[args.index(arg)] + '}';
		# print('s: ' + source);
		# print('d: ' + destination);
		result = result.replace(destination, source);
	return result;

while True:
	l = input('>> ');
	if l == '':
		break;

	result = re.search(macroRegex, l);
	if result:
		print(result.group("tag"));

		if result.group("arguments"):
			args = [arg.strip() for arg in result.group("arguments").split(',')];
			print(args);
			print(feed(macroBody, macroArgs, args));
	else:
		print('false');
	print('');
