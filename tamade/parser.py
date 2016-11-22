from __future__ import unicode_literals
import re

import logging


def parse_define(code):
    m = re.search('\(.*\)', code)
    try:
        raw_data_list = [value.strip() for value in m.group(0).strip("()").split(",") if value]
    except AttributeError:
        logging.error("[Parser]: Invalid Syntax -> {}".format(code))

    setting_name = raw_data_list[0]
    setting_value = raw_data_list[1]
    section = "core" if "." not in setting_name else setting_name.split('.')[0]
    if '"' not in setting_name:
        logging.warning("[Parser]: name is not a string -> {}".format(code))
    if '"' not in setting_value and "NULL" != setting_value:
        logging.warning("[Parser]: value is not a string -> {}".format(code))

    setting_pair = {
        "section": section.strip("\""),
        "name": setting_name.strip("\""),
        "value": setting_value.strip("\"")
    }

    return setting_pair


def parse_line(line):
    try:
        info, code = line.split(":")
    except ValueError:
        logging.debug("[Preprocessor]: can not find ':'-> {}".format(line))
        code = line

    if not code.strip():
        return None

    if "PHP_INI_BEGIN" in code or "ZEND_INI_BEGIN" in code:
        return None
    elif "PHP_INI_END" in code or "ZEND_INI_END" in code:
        return None
    else:
        return parse_define(code)


def parse_intermediate(intermediate_data):
    setting_pairs = []
    raw_data = intermediate_data
    for raw_data_line in raw_data.split("\n"):
        setting_pair = parse_line(raw_data_line)
        if setting_pair is None:
            continue
        setting_pairs.append(setting_pair)
    return setting_pairs
