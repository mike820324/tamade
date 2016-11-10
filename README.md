## tamade:

A simple command line utility tool that will grab every PHP ini settings from C source code.

## Installation:

- Requirements:

This tool currently rely on the ag(the silver searcher) to grep the C source code.
Make sure **ag** is installed in your system.


```bash
git clone https://github.com/mike820324/tamade
cd tamade
pip install -U tamade
```


## Quickstart:

The default formatter will use the json format.

```bash
# print to console
tamade --in-folder ${PHP_SRC_CODE} --pretty-print

# output to file
tamade --in-folder ${PHP_SRC_CODE} --pretty-print --out-file ${OUTPUT_FILE}
```


## License:

MIT
