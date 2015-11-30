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
            ap.add_option_mapping('A', 'auth')
            ap.add_option_mapping('S', 'session')
            ap.add_option_description('auth', 'Specify auth log bucket')
            ap.add_option_description('A', 'See also: auth')
            ap.add_option_description('session', 'Specify session log bucket')
            ap.add_option_description('S', 'See also: session')
            ap.add_option_type('auth', ArgumentParser.OPTION_SINGLE)
            ap.add_option_type('session', ArgumentParser.OPTION_SINGLE)

        self.__config = loader.get_module_by_base("config").get_configuration()

        self.register_subcommand("dump", self.log_dump)
        self.register_subcommand("show", self.log_show)

    def log_dump(self, *args, **kw):
        """ log:dump [--auth|-A] [--session|-S]

            Dumps raw log data out of Redis to the console.
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

        log_grab = []
        if argparser.options.get('auth', None):
            bucket = lb_conf.get_string('auth', 'log:auth')
            log_grab.append("%s%s" % (rd_prefix, bucket))

        if argparser.options.get('session', None):
            bucket = lb_conf.get_string('session', 'log:session')
            log_grab.append("%s%s" % (rd_prefix, bucket))

        for bucket in log_grab:
            logs = rdc.lrange(bucket, 0, -1)
            for log in logs:
                print log

    def log_show(self, *args, **kw):
        """ log:show [--auth|-A] [--session|-S]

            Dumps pretty log data out of Redis to the console.
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

        log_grab = []
        if argparser.options.get('auth', None):
            bucket = lb_conf.get_string('auth', 'log:auth')
            log_grab.append("%s%s" % (rd_prefix, bucket))

        if argparser.options.get('session', None):
            bucket = lb_conf.get_string('session', 'log:session')
            log_grab.append("%s%s" % (rd_prefix, bucket))

        for bucket in log_grab:
            logs = rdc.lrange(bucket, 0, -1)
            for log in logs:
                log = json.loads(log)
                print json.dumps(log, indent = 2, sort_keys = True)

