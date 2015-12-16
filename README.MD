# Thing
This pretty much just takes my weird, blockbased syntax and turns it into HTML. Probably not robust at all, to be honest. Uses forbiddenfruit (https://github.com/clarete/forbiddenfruit), lambdatools (which is just my own set of "I'm lazy" things), and dirtools (which again, is just some of my tools). As always, nothing guaranteed to work or whatever, and I take no responsibility for harm done to your person, computer or other belongings. Fly safe.

# Macros
Woo, stop repeating your shit over and over.

    def link-css(file):
    	link; rel=stylesheet; type=text/css; href=css/{file}.css

# Blocks
Woo, stop using end tags.

    html
    	body
    		div
    			span: Hi!
    			span: What's up!

# Sample

    def link-css(file):
    	link; rel=stylesheet; type=text/css; href=css/{file}.css

    def link-js(file):
    	script; type=text/javascript; src=js/{file}.js

    html
    	head
    		title: Sample title!
    		link-css(main)
    	body
    		div#with-an-id.and-a-class: I have an ID and a class!
    		div
    			span#a-child: I'm a child!
    			span: I'm another child!
    			div
    				span: I'm a a child inside another child, gruesome!
    		div#another-div
    			a; href=http://google.com: I'm a link!

Becomes

    <html>
    	<head>
    		<title>
    			Sample title!
    		</title>
    		<link href="css/main.css" type="text/css" rel="stylesheet" />
    	</head>
    	<body>
    		<div id="with-an-id.and-a-class">
    			I have an ID and a class!
    		</div>
    		<div>
    			<span id="a-child">
    				I'm a child!
    			</span>
    			<span>
    				I'm another child!
    			</span>
    			<div>
    				<span>
    					I'm a a child inside another child, gruesome!
    				</span>
    			</div>
    		</div>
    		<div id="another-div">
    			<a href="http://google.com">
    				I'm a link!
    			</a>
    		</div>
    	</body>
    </html>

# Todo
* Conditionals
* Variables
* Variable number of arguments to macros
* ???
