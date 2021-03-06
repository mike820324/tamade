from __future__ import unicode_literals
import copy
import argparse
import json

from intermediate import IntermediateGenerator
from preprosessor import preprocessing_intermediate
from parser import parse_intermediate

import logging


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


def start_parsing(mode,
                  php_src_path,
                  out_file=None,
                  ext_script_path=None,
                  pretty_print=False,
                  enable_ag=False):

    # Starting using ag to parse c source code to intermediate
    logging.info("[Main]: Parsing C source...")

    if enable_ag:
        _generator = "ag"
    else:
        _generator = "grep"

    intermediate_data = IntermediateGenerator.generate(
        php_src_path, generator=_generator)

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
    parser.add_argument(dest="php_src_path")
    advanced_group = parser.add_argument_group(
        "Advanced Settings", "Advanced Configuration for tamade")
    advanced_group.add_argument(
        "--parsing-stage", dest="stage", default="compile",
        choices=["intermediate", "preprocessing", "compile"],
        help="Choose different parsing stage")
    advanced_group.add_argument(
        "--ext-script", dest="ext_script_path",
        help="Specify the extension script path")
    advanced_group.add_argument(
        "--enable-ag", dest="enable_ag",
        action="store_true", default=False,
        help="Use the silver searcher to boost transforming performance")

    parser.add_argument("--out-file", dest="out_file")
    parser.add_argument(
        "--verbose-level", dest="verbose_level", default="info",
        choices=["critical", "error", "warning", "info", "debug", "notest"]
    )
    parser.add_argument(
        "--pretty-print", dest="pretty_print",
        action="store_true", default=False)


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
        options.pretty_print,
        options.enable_ag)
