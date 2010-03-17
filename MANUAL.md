This document describes the usage of the dml command line tool as well as the
syntax of dml files.

Usage
=====

If you type 'dml --help' on the command line, you should see something like
that:

<pre>

Usage: dml [options] FILE

Options:
  -h, --help   show this help message and exit
  -t, --html   generates HTML output
  -d, --dml    generates DML output
  -b, --debug  generates debug output
  -q, --quiet  don't print status messages to stdout

</pre>

FILE must be a valid dml-file. The next section describes the syntax of it. If
that file does not exist, dml with print an Error and exit.

The options might differ if you have other backends installed. What is always
there is '-q' or '--quiet', which supresses output in the console, and '-h' or
'--help' to show the help.

Any other option controls the various ouptuts. Each will write a file in the
working directory with the filename (without the '.dml' extension) + the
backend extension. For example:

$ dml --html path/to/my_funny_play.dml

will write a 'my_funny_play.html' into your current directory. Any existing
file named 'my_funny_play.html' in this directory will be overwritten.


Backends
--------

There are two kinds of backends: sinks and postprocessors. It's not too
difficult to write new backends; please consult the developers documentation if
you inted to do so.

Sinks directly feed off the parser (they are called sinks because it's a
streaming parser, and every event generated in the parser will eventually land
there, but they themselves don't generate or forward any event. They are the
end of the event food chain). They don't require third party tools to be
installed manually.

Sinks that come with dml:
- debug: useful for introspection if something goes wrong or when writing a
   new sink
- dml: transforms the dml into another dml. Yeah. Really.
- html: outputs a valid xhtml file
- latex: writes a nice latex file for further processing
- pdf: native pdf output, see e.g. LaTeX2pdf for a postprocessor outputting
   pretty pdfs

Postprocessors don't recieve any events from anything at all, they rely on
a sink to have done the dirty work. They just transform the output of a sink
into something else (usually a pdf). So you might have a LaTeX sink and a
LaTeX2pdf postprocessor, or a html sink and a html2pdf postprocessor. Post-
processors usually have a '2' in their name to indicate where they get their
source from. If a postprocessor is selected, it will automatically activate
it's corresponding sink, whether you selected it or not. Postprocessors usually
require a third party tool (like LaTeX). These tools may not be
automatically installed if you install dml. Refer to the READMEs in the 
'postprocessors' folder for installation help.

Postprocessors that come with dml:
- latex2pdf: like it says. Takes latex and boom! - pdf. Magic. Pure magic.

dml Syntax
==========

For a for more scientific explanation, look at developers documentation.


General Syntax
--------------

The dml is structured like a play usually is: First comes a title, then maybe a
text block for subtitle or abstract, then a number of informations like author,
date etc. The syntax for that is easy, like that:

    = My Funny Play =

    it's so funny

    *author* me
    *date* 03/04/2010

OK, that's:
- title enclosed in '='
- title, block and tag/value pairs separated by two newlines
- the tag in the tag/value line enclosed in '*'

Next may come the cast of the play. It may look like that:

    == Persons Involved ==

    *me* the funny author
    *you* the bored reader
    *the open source community*

En detail:
- cast title enclosed with '=='
- title, block and actor declaration/definition pairs separated by two newlines
etc.
Sounds familiar? Yes, the syntax is the same, it just means something different.

OK, a play needs some content, starting with an act title. Lo and behold:

    === Act I ===

    it was a dark and stormy night.

    *me* see? <smiles and waves> It's easy!
    *you* OK ...
        
    === Act II ===
    
    ==== Scene 1 ====

    *you* I'm gonna go. Now. <off>

    ==== Scene 2 ====
    
    The author stands alone on the stage.
    
    *me* Well then ... \\
    good bye!
    *the open source community* <is not very interested>

I guess by now you've got the hang of it. Act and scene titles are enclosed in
'===' and '====' respectively. Other notable things are inline stage
directions (they are enclosed with '<' and '>') and '\\', which forces a
linebreak, but no block separation. Good for poems and such.

How all of this will eventually be displayed is up to the backend.


Macros
---------

At any time you might write a macro, starting with '@', followerd by a
macro name and then a block delimited by '{' and '}'. Here's what they do:

#### meta ####
Used to declare metadata in key/value pairs. Only useful in the header of
the dml file. For example:

@meta table_of_contents: True
@meta paper_size: A5

Options may be separated by newlines or ';'

#TODO: list options

#### include ####
Include the contents of another dml-file in your play. Example:

@include a_part_of_a_play.dml

The file to be included must be in the directory of the parent file or in your
working (current) directory.


***

If you notice any errors in this document, please file a bug:
http://github.com/Ed-von-Schleck/dml/issues