import contextlib, malibu, os, pprint, sys
from contextlib import closing
from malibu.config import configuration
from malibu.text import table
from os.path import exists

from malibu.command import command_module, module
from malibu.text import ascii
from malibu.util import paths as pathutil


@command_module(
    name = "config",
    depends = []
)
class ConfigModule(module.CommandModule):

    BASE = "config"

    def __init__(self, loader):

        super(ConfigModule, self).__init__(base = ConfigModule.BASE)

        self.__loader = loader

        self.register_subcommand('get', self.config_get)
        self.register_subcommand('init', self.config_init)
        self.register_subcommand('set', self.config_set)
        self.register_subcommand('show', self.config_show)

        self.__config_paths = {
            '~/.lssoctl/config.ini',
            '/etc/lssoctl/config.ini'
        }

        self.__config = None
        self.__config_path = ''
        for path in self.__config_paths:
            path = pathutil.expand_path(path)
            fdir = pathutil.get_path_base(path)
            if not exists(fdir):
                try: os.mkdir(fdir)
                except: continue
            else:
                if not exists(path):
                    try:
                        with closing(open(path, 'w')) as config:
                            config.write("")
                    except: continue
                if os.access(path, os.R_OK | os.W_OK):
                    self.__config_path = path
                    self.__config = configuration.Configuration()
                    self.__config.load(path)
                else:
                    continue

        if self.__config is None:
            paths = ', '.join(self.__config_paths)
            raise module.CommandModuleException(
                "Could not open or create configuration file at paths: {}".format(paths))

    def get_configuration(self):
        """ Returns the configuration.Configuration instance used by
            this module.
        """

        return self.__config

    def config_get(self, *args, **kw):
        """ config:get [section].[key]

            Returns the named variable from the loaded configuration.
        """

        args = args[1:]

        try: var_path = args[0]
        except: raise CommandModuleException("Missing argument(s).")

        var_path = var_path.split('.')
        if len(var_path) > 2:
            var_path = var_path[0:2]

        if len(var_path) == 1: # Only the section specifier is given
            section_name = var_path[0]
            if not self.__config.has_section(section_name):
                print "Unknown configuration section '{}'.".format(
                    ascii.style_text(ascii.FG_GREEN, section_name))
                return
            else:
                section = self.__config.get_section(section_name)
                print 'Section [{}]:'.format(
                    ascii.style_text(ascii.FG_GREEN, section_name))
                for key, value in section.iteritems():
                    print '  {} -> {}'.format(key, value)
                print
        elif len(var_path) == 2: # Section and key specifier were given.
            section_name = var_path[0]
            if not self.__config.has_section(section_name):
                print "Unknown configuration section '{}'.".format(
                    ascii.style_text(ascii.FG_YELLOW, section_name))
                return
            else:
                section = self.__config.get_section(section_name)
                print 'Section [{}]:'.format(
                    ascii.style_text(ascii.FG_GREEN, section_name))
                key = var_path[1]
                value = section.get_string(key, None)
                if not value:
                    value = ascii.style_text(ascii.FG_RED, 'unset')
                print '  {} -> {}'.format(key, value)


    def config_init(self, *args, **kw):
        """ config:init []

            Initializes a default configuration in the current config path we've opened.
        """

        host = self.__config.add_section('lsso')
        host.set('api_endpoint', 'https://example.org/auth/api')

        redc = self.__config.add_section('redis')
        redc.set('host', 'example.org')
        redc.set('port', 6379)
        redc.set('secret', 'secret')
        redc.set('database', 0)
        redc.set('key_prefix', 'lsso:')

        credential = self.__config.add_section('credentials')
        credential.set('username', 'admin')
        credential.set('token', 'lsso auth token')

        print "{}".format(
            ascii.style_text(ascii.STYLE_BOLD, "Configuration initialized at {}.".format(
                ascii.style_text(ascii.FG_GREEN, self.__config_path))))

        self.__config.save(self.__config_path)

    def config_set(self, *args, **kw):
        """ config:set [section].[key] [value]

            Sets the named variable in the user configuration.
        """

        args = args[1:]

        try:
            var_path = args[0]
        except:
            raise CommandModuleException("Missing argument(s).")

        try:
            var_value = ' '.join(args[1:])
        except:
            raise CommandModuleException("Missing argument(s).")

        var_path = var_path.split('.')
        if len(var_path) > 2:
            var_path = var_path[0:2]

        if len(var_path) == 1: # Only the section specifier is given
            print 'Must provide a configuration node in the form of {} to set a value.'.format(
                ascii.style_text(ascii.BG_YELLOW, "section.key"))
            return
        elif len(var_path) == 2: # Section and key specifier were given.
            section_name = var_path[0]
            if not self.__config.has_section(section_name):
                print "Unknown configuration section '{}'.".format(
                    ascii.style_text(ascii.FG_YELLOW, section_name))
                return
            else:
                section = self.__config.get_section(section_name)
                print 'Section [{}]:'.format(
                    ascii.style_text(ascii.FG_GREEN, section_name))
                key = var_path[1]
                value = section.get_string(key, None)
                if not value:
                    value = ascii.style_text(ascii.FG_RED, 'unset')
                section.set(key, var_value)
                print '  {} => {} -> {}'.format(
                    key,
                    ascii.style_text(ascii.FG_RED, value),
                    ascii.style_text(ascii.FG_GREEN, var_value))

        self.__config.save(self.__config_path)

    def config_show(self, *args, **kw):
        """ config:show []

            Prints the current configuration.
        """

        for section_name in self.__config.sections():
            section = self.__config.get_section(section_name)
            print 'Section [{}]:'.format(
                ascii.style_text(ascii.FG_GREEN, section_name))
            for key, value in section.iteritems():
                print '  {} -> {}'.format(key, value)
            print ''

