import subprocess


def SilverSearcherGenerator(php_src_path):
    """Create intremediate format of php ini settings defination from c source code.

    The intermedate format is genereted by ag(the silver searcher)
    The format looks like follow:

    ex. generated by the silver searcher
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

    Args:
        php_src_path (str):  the php/pecl source code path.

    Return:
        data represent the intermediate representation string.
    """
    expression = '(?s)(ZEND|PHP)_INI_BEGIN.*(ZEND|PHP)_INI_END\(\)'
    command = 'ag -G "\c$." --nocolor --no-numbers "{0}" {1}'.format(
        expression, php_src_path)

    return subprocess.check_output(command, shell=True).decode("utf8")


def GrepGenerator(php_src_path):
    """Create intremediate format of php ini settings defination from c source code.

    The intermedate format is genereted by grep and find
    The format looks like follow:

        main/main.c:PHP_INI_BEGIN()
            STD_PHP_INI_ENTRY(...)
            STD_PHP_INI_BOOLEAN(...)
            STD_PHP_INI_ENTRY(...)
        PHP_INI_END()
        ext/test.c:PHP_INI_BEGIN()
            STD_PHP_INI_ENTRY(...)
            STD_PHP_INI_ENTRY(...)
            STD_PHP_INI_ENTRY(...)
            STD_PHP_INI_ENTRY(...)
        PHP_INI_END()

    Args:
        php_src_path (str):  the php/pecl source code path.

    Return:
        data represent the intermediate representation string.
    """
    expression = '(?s)(ZEND|PHP)_INI_BEGIN.*(ZEND|PHP)_INI_END\(\)'
    command = 'grep -Pzo "{0}" $(find {1} -name "*.c") || true'.format(
        expression, php_src_path)

    return subprocess.check_output(command, shell=True).decode("utf8")


class IntermediateGenerator(object):
    support_generators = {}

    @classmethod
    def add_generator(cls, name, func):
        cls.support_generators[name] = func

    @classmethod
    def generate(cls, php_src_path, generator="grep"):
        _generator = cls.support_generators[generator]
        return _generator(php_src_path)

IntermediateGenerator.add_generator("ag", SilverSearcherGenerator)
IntermediateGenerator.add_generator("grep", GrepGenerator)