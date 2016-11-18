from __future__ import unicode_literals
import copy
import argparse
import json

from parser import parse_c_source_to_intermediate, preprocessing_intermediate
from parser import parse_intermediate

import logging


def environment_check():
    """Check the necessary binary tools are installed

    Todo:
        Implement the detailed.

    Return:
        True: when environment checking passed
        False: when environment checking failed
    """
    return True


def load_script(filter_script_path):
    try:
        with open(filter_script_path) as fp:
            namespace = {"__file__": filter_script_path}
            code = compile(fp.read(), filter_script_path, "exec")
            exec(code, namespace, namespace)

    except Exception as e:
        logging.exception(e)

    return namespace


def pretty_formatter(php_settings):
    return json.dumps(php_settings, sort_keys=True, indent=4)


def start_parsing(mode, php_src_path, out_file=None, ext_script_path=None, pretty_print=False):
    # Starting using ag to parse c source code to intermediate
    logging.info("[Main]: Parsing C source...")
    intermediate_data = parse_c_source_to_intermediate(php_src_path)
    if mode == "intermediate":
        with open(out_file, "w") as fp:
            fp.write(intermediate_data.encode("utf8"))
        exit(0)

    # Preprocessing intermediate data.
    logging.info("[Main]: Preprocessing...")
    preprocessed_intermediate_data = preprocessing_intermediate(intermediate_data)
    if mode == "preprocessing":
        with open(out_file, "w") as fp:
            fp.write(preprocessed_intermediate_data.encode("utf8"))
        exit(0)

    # Transforming intermediate data into dict.
    logging.info("[Main]: Transforming...")
    php_settings = parse_intermediate(preprocessed_intermediate_data)

    logging.info("[Main]: Total Settings Number {}".format(
        len(php_settings)))

    # If user has specify extension script,
    # We load it and try to get the filter and formater function.
    if ext_script_path:
        script_ns = load_script(ext_script_path)
        try:
            filterer = script_ns["filter"]
        except KeyError:
            filterer = None

        try:
            formatter = script_ns["formatter"]
        except KeyError:
            if pretty_print:
                formatter = pretty_formatter
            else:
                formatter = json.dumps
    else:
        filterer = None
        if pretty_print:
            formatter = pretty_formatter
        else:
            formatter = json.dumps

    if filterer:
        logging.info("[Main]: Filtering extensions...")
        setting = filterer(copy.copy(php_settings))
    else:
        setting = php_settings

    output_data = formatter(setting)
    if out_file:
        with open(out_file, "w") as fp:
            fp.write(output_data)
    else:
        logging.info("\n" + output_data)


def create_options(parser):
    parser.add_argument(
        "--stage", dest="stage", default="compile",
        choices=["intermediate", "preprocessing", "compile"],
        help="Choose different parsing stage")
    parser.add_argument(
        "--ext-script", dest="ext_script_path",
        help="Specify the extension script path")
    parser.add_argument("--in-folder", dest="php_src_path", required=True)
    parser.add_argument("--out-file", dest="out_file")
    parser.add_argument(
        "--pretty-print", dest="pretty_print",
        action="store_true", default=False)
    parser.add_argument(
        "--verbose-level", dest="verbose_level", default="info",
        choices=["critical", "error", "warning", "info", "debug", "notest"]
    )


def main():
    parser = argparse.ArgumentParser(description="PHP ini setting extractor")
    create_options(parser)
    options = parser.parse_args()

    log_level = getattr(logging, options.verbose_level.upper())
    logging.basicConfig(level=log_level)

    start_parsing(
        options.stage,
        options.php_src_path, options.out_file,
        options.ext_script_path,
        options.pretty_print)
