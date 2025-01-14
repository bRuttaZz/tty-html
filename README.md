<img src="./misc/logo.png" align="right" width=150>

# \[Pre\]tty-HTML

**[Pre]tty-html: (the logo reads as: 'pookie html') A minimalist python script to pretty print html docs to unix terminal.**
Pipe the output of html generators to tty-html, for a neat terminal render (than a hard to decode xml dump).

[![pypi](https://img.shields.io/pypi/v/tty-html.svg)](https://pypi.org/project/tty-html/)
[![Release](https://img.shields.io/github/release/bruttazz/tty-html.svg)](https://github.com/bruttazz/tty-html/releases/latest)

## Usage

The program is intended to be just a simple Unix CLI utility. One can specify any html file as an input or pipe an html dump to the stdin of `tty-html` to get a readable pretty print.


```sh
# for detailed usage
$ tty-html --help
...

# format from an html file 
$ tty-html index.html
...

# format from stdin
$ curl https://some-website.com/blog -s | tty-html
...

```



## Installation

Easy! There're three ways

### 1. Compiled binary
head over to the [release page](https://github.com/bruttazz/tty-html/releases/latest) and download the binary. make it executable. Thats it. (optionally add it to a bin path of your choice)

### 2. Using PIP 
If you got pip, feel free to install  using
```sh
pip install tty-html
```

### 3. Build from source
If you are nerdy enough, there is a Makefile :), get a c compiler, install `python3` and `cython`, and go for the following commands in order
```sh
# transpile script to c
make 

# compile the c
make compile
```

for detailed use case : `make help` :)

## Usage Gallery

1. the raw html 
![raw image](./misc/demo.in.png)

2. the formatted one
![formatted](./misc/demo.out.png)