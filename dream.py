# TODO:
# Parse macros in source file.
# Split things up for readability, this is getting retarded.
# How do modules even work anyways, really.

import sys, lambdatools, dirtools, re;

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def halve(text, separator):
	split = text.split(separator);
	first = separator.join(split[:-1]);

	if len(split) > 1:
		return (first, split[-1]);
	else:
		return first, None;

# Not so much nontag, as ignored tag.
# I.e., something to remain exactly as html as written.
# E.g.
# html
#   head
#	   **<title>test</title>
# The title should not be parsed as a tag.
class NonTag():
	def __init__(self, content):
		# We require these to interact with the rest of our DOM.
		self.indent = Source.indentLevel(content);
		self.content = content.lstrip('\t')[2:];
		self.parent = None;

	def __str__(self):
		return '\t' * self.indent + self.content;

	def generate(self):
		return str(self);

def show(s):
	global switches;
	output = str(s);

	if '-s' in switches:
		output = output.replace('\t', '    ');

	print(output);

class Macro():
	macros = {};

	macroTagRegex = r'\w[\w\-_]+'
	valueRegex = r'\w+'

	macroRegex = ''.join([
		r'(?P<full>',
			# Tag itself
			r'(?P<macro>', macroTagRegex, r')', r'\s*',
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
			r'\s*', r'\)',
		r')'
	]);

	def __init__(self):
		self.name = None;
		self.args = [];
		self.body = None;

	def feed(self, line, matches):
		result = self.body;

		args = None;
		if matches.group("arguments"):
			args = [arg.strip() for arg in matches.group("arguments").split(',')];

		for arg in args:
			source = arg;
			destination = '{' + self.args[args.index(arg)] + '}';
			result = result.replace(destination, source);

		return re.sub(Macro.macroRegex, result, line);

class Tag():
	@staticmethod
	def parse(source):
		"""Take a tag in the form of tag.class#id
		and create an object from it"""

		# If we're a nontag...
		if source.lstrip('\t')[0:2] == '**':
			return NonTag(source);

		tag = "";
		tagclass = "";
		tagid = "";
		content = "";
		attributes = [];
		selfclosing = False;

		indent = Source.indentLevel(source);
		source = source.lstrip();

		if ': ' in source:
			source, content = halve(source, ': ');

		while '; ' in source:
			source, attribute = halve(source, '; ');
			key, value = halve(attribute, '=');
			attributes.append((key, value));


		if '#' in source:
			source, tagid = halve(source, '#');

		if '.' in source:
			source, tagclass = halve(source, '.');

		tag = source;

		selfclosers = [
				'area', 'base', 'br', 'col', 'command', 'embed', 'hr', 'img',
				'input', 'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr'
		];

		if tag in selfclosers:
			selfclosing = True;

		return Tag(tag, tagclass, tagid, content, indent, attributes, selfclosing);

	def __init__(self, tag, tagclass, tagid, content, indent, attributes, selfclosing):
		self.tag = tag;
		self.tagclass = tagclass;
		self.tagid = tagid;
		self.content = content;
		self.indent = indent;
		self.children = [];
		self.parent = None;
		self.attributes = attributes;
		self.selfclosing = selfclosing;

	def __str__(self):
		return self.generate();

	def __repr__(self):
		return self.generate().lstrip('\t');

	def adopt(self, child):
		self.children.append(child);
		child.parent = self;

	def generate(self):
		global switches;
		spaces = '    ';

		keys = {};
		formatstring = '{indent}<{tag}';

		keys['indent'] = '\t' * self.indent;
		keys['tag'] = self.tag;

		if any(self.tagclass):
			formatstring += ' class=\"{tagclass}\"';
			keys['tagclass'] = self.tagclass;

		if any(self.tagid):
			formatstring += ' id=\"{tagid}\"';
			keys['tagid'] = self.tagid;

		for attribute in self.attributes:
			formatstring += ' ' + attribute[0] + '="' + attribute[1] + '"';

		if self.selfclosing:
			formatstring += ' />';

			result = formatstring.format(**keys);

			if '-s' in switches:
				result = result.replace('\t', spaces);

			return result;

		formatstring += '>';

		content = '';
		if any(self.content):
			formatstring += '\n{indent}\t{content}';
			keys['content'] = self.content;

		children = '';
		if any(self.children):
			formatstring += '\n{children}';
			keys['children'] = '\n'.join([child.generate() for child in self.children]);

		if any(self.children) or any(self.content):
			formatstring += '\n{indent}';

		formatstring += '</{tag}>';

		return formatstring.format(**keys);

class Source():
	@staticmethod
	def flatten(blocks):
		blockstack = list(blocks);

		blockstack = blockstack[:-1];

		return blockstack;

	@staticmethod
	def printblocks(blocks):
		print();
		for block in blocks:
			print(str(block) + '\n');
		print();

	@staticmethod
	def parse(source, indent = 0):
		macros = {};

		test = Macro();
		test.name = 'test';
		test.args = ['test'];
		test.body = 'span: {test}';
		Macro.macros['test'] = test;

		source = [line for line in source if line != ''];
		for i in range(0, len(source)):
			line = source[i];
			matches = re.search(Macro.macroRegex, line);
			if matches:
				source[i] = Macro.macros[matches.group('macro')].feed(line, matches);

		indents = [Source.indentLevel(line) for line in source];
		blockstack = [];
		currentdent = None;

		tags = [Tag.parse(line) for line in source];

		for index in range(0, len(source)):
			line = source[index];
			tag = tags[index];

			pardent = blockstack[-1].indent if len(blockstack) > 0 else 0;

			if isDebugging():
				print(tag.tag + ', indent: ' + str(tag.indent));

			# Root
			if len(blockstack) == 0:
				if isDebugging():
					print('root');

				blockstack.append(tag);
			else:
				if tag.indent > pardent:
					blockstack[-1].adopt(tag);
					blockstack.append(tag);

					if isDebugging():
						print('indent');
						print(blockstack[0]);
				elif tag.indent == pardent:
					blockstack[-1].parent.adopt(tag);
					blockstack.append(tag);

					if isDebugging():
						print('element');
						print(blockstack[0]);
				else:
					if isDebugging():
						print('our dent ' + str(tag.indent));

					ourparent = None;
					for subindex in range(index - 1, -1, -1):
						if tags[subindex].indent < tag.indent:
							if isDebugging():
								print('found parent!: ' + tags[subindex].tag);
							tag.parent = tags[subindex];
							tag.parent.adopt(tag);
							break;

					if isDebugging():
						print('dedent');
						print(blockstack[0]);
						print('blockstack:');
						[print('===\n' + str(block) + '\n') for block in blockstack];

					parentindex = blockstack.index(tag.parent);
					blockstack = blockstack[:parentindex + 1];
					blockstack.append(tag);
				if isDebugging():
					print('par: ' + str(tag.parent.tag) + ' ' + str(tag.parent.tagid));

			if isDebugging():
				print('len bs: ' + str(len(blockstack)) + '=======================================\n');

		if isDebugging():
			print('end\n');

		# Final dedent
		blockstack = blockstack[:1];

		if '-p' in switches:
			output = str(blockstack[0]).split('\n');
			for index in range(0, len(output)):
				if '-ln' in switches:
					print(str(index + 1).rjust(4) + ' ', end = "");
				show(output[index]);

		return blockstack[0];

	@staticmethod
	def indentLevel(line):
		return len(line) - len(line.lstrip('\t'));

def isDebugging():
	global switches;
	if '-d' in switches:
		return True;
	return False;

switches = [];
if __name__ == '__main__':
	args = sys.argv;

	# If we're piped...
	if not sys.stdin.isatty():
		for line in sys.stdin:
			args.append(line.rstrip());

	lambdatools.setup();

	switches = args.where(lambda a: a[0] == '-');
	args = args.where(lambda a: a not in switches);

	if len(args) < 2:
		print('Need more arguments!');
	else:
		for sourcefile in args[1:]:
			source = [];

			with open(sourcefile) as f:
				for line in f:
					source.append(line.rstrip('\n'));

			if '-b' in switches:
				print(bcolors.WARNING + 'Before:' + bcolors.ENDC);
				[show(line) for line in source];
				print(bcolors.WARNING + '\nAfter:' + bcolors.ENDC);

			source = source.where(lambda l: line.strip() != '');
			result = Source.parse(source);

			# If not just printing.
			if not '-p' in switches:
				outname = dirtools.getName(sourcefile).replace('.dml', '.html');
				path = dirtools.getDirectory(sourcefile) + '\\' + outname;

				with open(path, 'w') as out:
					out.write(str(result));
