# !!! info "Pylliterate"
#     Pylliterate is a Python library for crafting self-documenting code,
#     loosely following the literate programming paradigm.
#     The library itself is coded following pylliterate "best practices",
#     so by reading this, either in source code or in the rendered documentation,
#     you should be able to understand what we want to achieve.
#     If you don't, then we have done a pretty bad job.


# The basic idea is that code should be self-explanatory, but not in
# the sense that it doesn't require comments. Rather, it should be
# self-explanatory because comments and code together flow naturally and
# interweave with each other in a manner that is easy to read by people
# beyond those who wrote it.

# This means that comments should be writen in prose, with correct grammar,
# and not in short phrases next to some instructions without any context.
# It should be pleasing to read.

# This also means that you are forced to organize your source code in a way
# that allows the narrative to flow. For example, it will force you to put
# the most important definitions (clases and methods) at the top, and leave
# implementation details for the end.

# I know some will complain, and say "but why am I forced to organize my code in a specific way!?".
# Well, there is no real restriction to organizing code in Python other than for scoping rules,
# i.e., that any symbol you use is already defined before. Other than that, you either don't care
# how the code is organized, in which case it is better to have some guidelines, or you do
# care how your code is organized. In this second case, if the way your code is organized is not already
# optimized for readability, then my opinion is that you're organizing it wrong. Plain and simple.

# With pylliterate, you always organize your code in the way that best fits the explanation.
# And when you are required to import something or define something at some point, then you better
# have a good excuse for including it there. If you're doing it right, you should have already
# explained your why's, and you should be fairly justified at that point.

# To get in the right mindset for this paradigm shift, think of your source in the following terms.
# You are a narrator talking to yourself (the future you), trying to explain how this code works.
# Instead of the code being the important thing, is the narrative what matters.
# The code just happens to be inserted into some points of the narrative to actually do what the
# narrative says.

# There are many ways to explain an idea, but one of the most successful from my point of view is
# by trying to answer the following questions, in order: why, what, and how.
# Always start with the motivation, **why** is code necessary, to solve which problem?
# Then move to the proposed solution, **what** are you actually going to do, which are the components of the solution?
# And then add the implementation details: **how** is each subtask implemented?

# There are many advantages to this idea. Two of the most important ones are:

# - Anyone reading this code in the future should be able to understand it, specially because
#   now not only the implementation details are there, but also all the motivation behind choosing some
#   approach rather than another.

# - It will make much easier for yourself to actually develop the project because it will
#   force you to think about the problem you want to solve before thinking about the solution. And it will
#   force you to write down explicitly what is that problem, what is the expected solution, which are the main
#   assumptions.

# ## Writing as a pylliterate

# Now let's talk about using pylliterate. As you have seen so far, these are just regular comments in the code.
# That's it, nothing has changed. You just need the right mindset.

# Each comment will be parsed and ultimately rendered as Markdown, so you are free to include any Markdown
# styling that you want, including lists, **bold**, `code`, and even sections (using `##`).
# At the beginning of this file you can see the docstrings. They are rendered exactly the same in the final
# documentation as regular Markdown, but since they also serve as the internal documentation of this module
# for IntelliSense purposes, you have to decide how much narrative do you want to be part of the "core" documentation.

# And then you just add the code as always. Illiterate Python files are just regular Python files,
# so everything should work the same as before.

# ## High-level implementation

# Illiterate is a very simple program. All it does is parse Python files, which are converted to some
# intermediate representation, and then writes them back in Markdown. However, this "parsing" is very simple,
# because we don't really need to understand the Python code. We just need to separate a file into blocks
# of Markdown and blocks of Python, and then write that back.
# There is some nuance here, to be fair, because we do want to handle some low-level annotations, like
# references to existing types and members, but we'll get there pretty soon.

# To organize this process, we will have classes that represent the different types of content,
# and then a very simple parser that scans a file top-to-bottom and builds the corresponding block.
# At this point, however, we only care about the high-level architecture.

# Starting at root folder, we will process all the `.py` files in sequence, producing for each one
# a markdown file that will be saved to the output folder.

# ### The outer loop

# In the output, filenames will match the folder structure that we find, only changing the
# `.py` with an `.md` extension and every "/" with a dot.
# For example `src/moduleA/moduleB/file.py` will become `output/moduleA.moduleB.file.md`.
# We will use `pathlib.Path` for that purpose.

import shutil
from pathlib import Path
from rich.progress import track
from pylliterate.config import PylliterateConfig
from .core import Parser
# Next comes our top level functions that processes each file.
# Notice how we also have docstrings in each function, as usual.
# Docstrings are for guiding developers when inspecting our code via IntelliSense and such.
# Hence, they should be fairly self-contained.

# You will also notice that methods have comments, as usual. However, inline comments do not
# lend themselves very well to a coherent and flowing narrative. They are better suited to
# explain very concise ideas.
# For this reason, pylliterate won't render those comments as Markdown. They are an integral part
# of your code, and will be rendered as code.
# If you want to render them as Markdown, you will have to explicitly pass `--inline` in the CLI.

# Hence, you will be forced to refactor your methods so that they are as small as possible.
# That way, they will have as little comments as possible, ideally none, because the surrounding
# comments are already enough to make everything as clear as it needs to be.
# If a method, including comments, is longer than one screen of text, consider refactoring it.

# ### Processing each file

# Processing a single file is quite straightforward as well.
# We will be using a [`Parser`](ref:pylliterate/core:Parser) class that does all the heavy-lifting.
# We feed the parser with the input, and it will return an object (of type [`Content`](ref:pylliterate/core:Content))
# that knows how to write itself into a file in Markdown.
# Note that we just used two internal references in the previous sentences. We'll see how these special constructions
# are handled when look at the parser implementation but, spoiler alert, it involves some regex.
# Be aware of the  [`PylliterateConfig`](ref:pylliterate/config:PylliterateConfig) class that hold parameters needed
# in each processing file


def process(input_path: Path, output_path: Path, konfig: PylliterateConfig):
    # We need to create this folder hierarchy if it doesn't exist:
    output_path.parent.mkdir(exist_ok=True)

    # First we check if this is just a regular copy
    if input_path.suffix != ".py":
        shutil.copy(input_path, output_path)
        return

    # Otherwise, we parse, passing also the file name.
    with input_path.open() as fp:
        content = Parser(
            fp, config=konfig, module_name=input_path.name, location=input_path.parent
        ).parse()

    # And then we dump the parsed content.
    with output_path.open("w") as fp:
        content.dump(fp)


# Now is easy process all configured files at once

def process_all(cfg: PylliterateConfig):
    files = list(cfg.files)
    # This function does all the heavy-lifting...
    for input_path, output_path in track(files):
        process(input_path, output_path, cfg)

# And that's it. As you can see, being forced to describe our process in this way also
# forces us to write pretty small methods, and to organize our code in the way that is
# easier to explain. This might seem daunting at first, but believe me (and thousands of
# computer scientists and software engineers that have been saying this for decades),
# every effort that you take now to make your code more readable will be paid in the future
# when you have to come back.

# ## Where to go from here?

# As you have seen, pylliterate makes no assumption about the order in which your files will be read.
# If you want to force a particular order, that goes into your `mkdocs.yml`
# (or wherever your documentation engine says). However, since this is Markdown, you can include
# links anywhere you want, since only you know how your documentation engine generates links.

# Illiterate automatically generates anchors for top-level definitions of classes and methods, in
# the form `ref:module:ClassName` or `ref:module:method_name`.
# As an example, you can read more about the [`Parser`](ref:pylliterate/core:Parser)
# (which is an auto-generated link)
# or you can directly see [how the CLI works](ref:pylliterate/cli).
