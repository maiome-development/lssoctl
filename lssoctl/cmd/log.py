import json, malibu, redis
from malibu.command import command_module, module
from malibu.text import ascii
from malibu.util.args import ArgumentParser


@command_module(
    name = "log",
    depends = ["config"]
)
class LogModule(module.CommandModule):

    BASE = "log"

    def __init__(self, loader):

        super(LogModule, self).__init__(base = LogModule.BASE)

        self.__loader = loader

        with self.__loader.get_argument_parser() as ap:
            ap.add_option_mapping('P', 'pretty')

            ap.add_option_description('pretty', 'Pretty print output')
            ap.add_option_description('P', 'See also: pretty')

            ap.add_option_type('auth', ArgumentParser.OPTION_SINGLE)
            ap.add_option_type('api', ArgumentParser.OPTION_SINGLE)
            ap.add_option_type('session', ArgumentParser.OPTION_SINGLE)
            ap.add_option_type('pretty', ArgumentParser.OPTION_SINGLE)

        self.__config = loader.get_module_by_base("config").get_configuration()

        self.register_subcommand("view", self.log_view)

    def log_view(self, *args, **kw):
        """ log:view [--pretty|-P] [list,of,buckets]

            Dumps log data out of Redis.
            Requires config section [redis] to be populated and valid.
        """

        if 'args' in kw:
            argparser = kw['args']
        else:
            argparser = self.__loader.get_argument_parser()

        redis_conf = self.__config.get_section('redis')
        lb_conf = self.__config.get_section('log_buckets')

        rdc = redis.StrictRedis(
            host = redis_conf.get_string('host', 'localhost'),
            port = redis_conf.get_int('port', 6379),
            password = redis_conf.get_string('secret', None),
            db = redis_conf.get_int('database', 0))

        rd_prefix = redis_conf.get_string('key_prefix', 'lsso:')

        # parameter arrangement:
        #  0  - script name
        #  1  - subcommand name
        #  2: - arguments to subcommand
        try: buckets = argparser.parameters[2]
        except (IndexError) as e:
            return False

        buckets = buckets.split(",")

        for _bucket in buckets:
            bucket = "%slog:%s" % (rd_prefix, _bucket)
            logs = rdc.lrange(bucket, 0, -1)
            fulllog = []
            for log in logs:
                fulllog.append(json.loads(log))

            if argparser.options.get('pretty', False):
                _logs = {"%s_log" % (_bucket): fulllog}
                print json.dumps(_logs, indent = 2, sort_keys = True)
            else:
                _logs = {"%s_log" % (_bucket): fulllog}
                print _logs

