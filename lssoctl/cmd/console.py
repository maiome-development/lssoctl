import logging, malibu, os, sys, traceback

from malibu import command
from malibu.command import module
from malibu.util import args
from malibu.util import log

def command_main():
    """ Entry point for calling lssoctl from the command line.
    """

    argparser = args.ArgumentParser.from_argv()
    argparser.set_default_param_type(argparser.PARAM_LONG,
                                     argparser.OPTION_PARAMETERIZED)

    argparser.add_option_mapping('c', 'config')
    argparser.add_option_type('c', argparser.OPTION_PARAMETERIZED)
    argparser.add_option_description('c', 'See also: --config')

    argparser.add_option_type('config', argparser.OPTION_PARAMETERIZED)
    argparser.add_option_description('config', 'Path to configuration file.')

    argparser.add_option_mapping('D', 'debug')
    argparser.add_option_type('D', argparser.OPTION_SINGLE)
    argparser.add_option_description('D', 'See also: --debug')

    argparser.add_option_type('debug', argparser.OPTION_SINGLE)
    argparser.add_option_description('debug', 'Print logging messages to stdout.')

    modloader = module.CommandModuleLoader(argparser)

    mods = command.get_command_modules(package = __package__)
    modloader.register_modules(mods.values())
    modloader.instantiate_modules()

    argparser.parse()

    if len(argparser.parameters) < 2:
        argparser.parameters.append('help:all')

    try:
        debug = argparser.options['debug']
    except:
        debug = False

    log.LoggingDriver(
        logfile = '/tmp/lssoctl.log',
        loglevel = logging.DEBUG,
        stream = debug,
        name = "lssoctl")

    logger = log.LoggingDriver.find_logger()

    modloader.parse_command(
        argparser.parameters[1],
        *argparser.parameters[1:],
        args = argparser)

    modloader.deinit_modules()
