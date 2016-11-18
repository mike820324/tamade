from __future__ import unicode_literals
import subprocess
import re
from comments import Comments

import logging
logging.basicConfig(level=logging.DEBUG)


def parse_c_source_to_intermediate(php_src_path):
    """Create intremediate format of php ini settings defination from c source code.

    The intermedate format is genereted by ag(the silver searcher)
    The format looks like follow:

        main/main.c:PHP_INI_BEGIN()
        main/main.c:	STD_PHP_INI_ENTRY(...)
        main/main.c:	STD_PHP_INI_BOOLEAN(...)
        main/main.c:	STD_PHP_INI_ENTRY(...)
        main/main.c:PHP_INI_END()
        ext/test.c:PHP_INI_BEGIN()
        ext/test.c:	STD_PHP_INI_ENTRY(...)
        ext/test.c:	STD_PHP_INI_ENTRY(...)
        ext/test.c:	STD_PHP_INI_ENTRY(...)
        ext/test.c:	STD_PHP_INI_ENTRY(...)
        ext/test.c:PHP_INI_END()

    Note: Currently this method require the ag(the silver searcher) avaliable.

    Args:
        php_src_path (str):  the php/pecl source code path.

    Return:
        data represent the intermediate representation string.
    """

    expression = '(?s)(ZEND|PHP)_INI_BEGIN.*(ZEND|PHP)_INI_END'
    command = 'ag --ignore "*.h" --nocolor --no-numbers "{0}" {1}'.format(
        expression, php_src_path)
    return subprocess.check_output(command, shell=True).decode("utf8")


def preprocessing_intermediate_remove_blank_line(intermediate_data):
    """Preprocessing intermediate data: Remove blank line"""
    for line in intermediate_data.split("\n"):
        if not line.strip():
            continue

        try:
            info, code = line.split(":")
        except ValueError:
            logging.error("[Preprocessor]: Incorrect line format -> {}".format(line))

        if not code.strip():
            continue
        yield line


def preprocessing_intermediate_combine_continue_line(intermediate_data):
    """Preprocessing intermediate data: Combine continue line"""
    prev_lines = []
    is_continue = False
    for line in intermediate_data.split("\n"):
        try:
            info, code = line.split(":")
        except ValueError:
            logging.error("[Preprocessor]: Incorrect line format -> {}".format(line))
            continue

        code = code.strip()
        if not code:
            continue

        if not is_continue:
            if "(" in code and ")" == code[-1]:
                yield line

            elif "(" in code and ")" != code[-1]:
                logging.debug("[Preprocessor]: incomplete line -> {}".format(code))
                prev_lines.append(code)
                is_continue = True
            else:
                logging.error("[Preprocessor]: Incorrect line format -> {}".format(line))


        else:
            if ")" == code[-1]:
                prev_lines.append(code)
                complete_code = "".join(prev_lines)
                prev_lines = []
                complete_line = "{0}:{1}".format(info, complete_code)
                is_continue = False
                logging.debug("[Preprocessor]: complete line -> {}".format(complete_code))
                yield complete_line
            else:
                logging.debug("[Preprocessor]: append line -> {}".format(code))
                prev_lines.append(code)


def preprocessing_intermediate_remove_c_define(intermediate_data):
    for line in intermediate_data.split("\n"):
        try:
            info, code = line.split(":")
        except ValueError:
            logging.error("[Preprocessor]: Incorrect line format -> {}".format(line))
            continue

        code = code.strip()
        if not code:
            continue

        if "#" != code[0]:
            yield line
        else:
            logging.debug("[Preprocessor]: Remove C define -> {}".format(code))


def preprocessing_intermediate_remove_comment(intermediate_data):
    """Preprocessing intermediate data: Remove comment"""
    remover = Comments(style="c")
    data = remover.strip(intermediate_data)
    return data


def preprocessing_intermediate(intermediate_data):
    data = intermediate_data

    data = "\n".join(preprocessing_intermediate_remove_blank_line(data))
    data = preprocessing_intermediate_remove_comment(data)
    data = "\n".join(preprocessing_intermediate_remove_c_define(data))
    data = "\n".join(preprocessing_intermediate_combine_continue_line(data))

    return data


def parse_define(info, code):
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
        logging.error("[Parser]: Invalid syntax -> {}".format(line))
        return None

    if "PHP_INI_BEGIN" in code or "ZEND_INI_BEGIN" in code:
        return None
    elif "PHP_INI_END" in code or "ZEND_INI_END" in code:
        return None
    else:
        return parse_define(info, code)


def parse_intermediate(intermediate_data):
    setting_pairs = []
    raw_data = intermediate_data

    for raw_data_line in raw_data.split("\n"):
        setting_pair = parse_line(raw_data_line)
        if setting_pair is None:
            continue
        setting_pairs.append(setting_pair)

    return setting_pairs
