from comments import Comments
import logging


def preprocessing_intermediate_remove_blank_line(intermediate_data):
    """Preprocessing intermediate data: Remove blank line"""
    for line in intermediate_data.split("\n"):
        if not line.strip():
            continue

        try:
            info, code = line.split(":")
        except ValueError:
            logging.debug("[Preprocessor]: can not find ':'-> {}".format(line))
            code = line

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
            logging.debug("[Preprocessor]: can not find ':'-> {}".format(line))
            code = line

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
                complete_line = "{}".format(complete_code)
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
            logging.debug("[Preprocessor]: Incorrect line format -> {}".format(line))
            code = line

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

    data = preprocessing_intermediate_remove_comment(data)
    data = "\n".join(preprocessing_intermediate_remove_blank_line(data))
    data = "\n".join(preprocessing_intermediate_remove_c_define(data))
    data = "\n".join(preprocessing_intermediate_combine_continue_line(data))

    return data
