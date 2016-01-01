import datetime
import redis
from malibu.command import command_module, module
from malibu.text import ascii, table


@command_module(
    name="session",
    depends=["config"]
)
class SessionModule(module.CommandModule):

    BASE = "session"

    def __init__(self, loader):

        super(SessionModule, self).__init__(base=SessionModule.BASE)

        self.__loader = loader

        self.__config = loader.get_module_by_base("config").get_configuration()

        self.register_subcommand("list", self.session_list)
        self.register_subcommand("info", self.session_info)
        # self.register_subcommand("create", self.session_create)
        self.register_subcommand("revoke", self.session_revoke)

    def session_list(self, *args, **kw):
        """ session:list [--no-table]

            Lists all open LSSO sessions in Redis.
            Requires config section [redis] to be populated and valid.
        """

        if 'args' in kw:
            argparser = kw['args']
        else:
            argparser = self.__loader.get_argument_parser()

        redis_conf = self.__config.get_section('redis')

        rdc = redis.StrictRedis(
            host=redis_conf.get_string('host', 'localhost'),
            port=redis_conf.get_int('port', 6379),
            password=redis_conf.get_string('secret', None),
            db=redis_conf.get_int('database', 0))

        rd_prefix = redis_conf.get_string('key_prefix', 'lsso:')

        session_list = rdc.keys(rd_prefix + "session:*")
        sessions = {}
        for session in session_list:
            stok = session.split(':')[2]
            session_data = rdc.hgetall(session)
            sessions.update({stok: session_data})

        if len(sessions) == 0:
            print ascii.style_text(
                ascii.FG_RED,
                "No sessions open.")
            return False

        if argparser.options.get('no-table', False):
            for stok, sdat in sessions.iteritems():
                print "%s\t%s\t%s" % (
                    stok,
                    sdat.get('username', 'unknown'),
                    sdat.get('created', 'unknown'))
        else:
            headers = [
                "Session Token",
                "User",
                "Created"
            ]

            tt = table.TextTable()
            tt.add_header_list(headers)
            rows = []
            for stok, sdat in sessions.iteritems():
                rows.append(
                    (stok,
                     sdat.get('username', 'unknown'),
                     sdat.get('created', 'unknown'),))

            tt.add_data_ztup(rows)

            for line in tt.format():
                print line

    def session_info(self, *args, **kw):
        """ session:info [session_id]

            Show all information for a session.
            Requires config section [redis] to be populated and valid.
        """

        if 'args' in kw:
            argparser = kw['args']
        else:
            argparser = self.__loader.get_argument_parser()

        redis_conf = self.__config.get_section('redis')

        rdc = redis.StrictRedis(
            host=redis_conf.get_string('host', 'localhost'),
            port=redis_conf.get_int('port', 6379),
            password=redis_conf.get_string('secret', None),
            db=redis_conf.get_int('database', 0))

        rd_prefix = redis_conf.get_string('key_prefix', 'lsso:')

        try:
            session_id = argparser.parameters[2]
        except (IndexError) as e:
            print ascii.style_text(
                ascii.FG_RED,
                "session:info requires a session_id to query.")
            return False

        session_key = rd_prefix + "session:" + session_id

        session = rdc.hgetall(session_key)
        if not session:
            print ascii.style_text(
                ascii.FG_RED,
                "No such session: %s" % (session_id))
            return False

        # Convert session[created] to datetime from Unix TS
        creat_ts = float(session['created'])
        try:
            session.update({
                "created": datetime.datetime.fromtimestamp(creat_ts),
            })
        except ValueError:
            pass

        expire_time = datetime.datetime.now() + datetime.timedelta(
            milliseconds=rdc.pttl(session_key))
        session.update({"expires": expire_time})

        print "%s ->" % (session_id)
        for k, v in session.iteritems():
            print "  %12s => %s" % (k, v)

    def session_create(self, *args, **kw):
        """ session:create [--username [...]] [--password [...]] [--prompt-pass|-W] [--scope [...]]

            Create a new session and return the ID.
            Requires config section [redis] to be populated and valid.
        """

        pass

    def session_revoke(self, *args, **kw):
        """ session:revoke [session_id]

            Revoke a session with the given id.
            Requires config section [redis] to be populated and valid.
        """

        if 'args' in kw:
            argparser = kw['args']
        else:
            argparser = self.__loader.get_argument_parser()

        redis_conf = self.__config.get_section('redis')

        rdc = redis.StrictRedis(
            host=redis_conf.get_string('host', 'localhost'),
            port=redis_conf.get_int('port', 6379),
            password=redis_conf.get_string('secret', None),
            db=redis_conf.get_int('database', 0))

        rd_prefix = redis_conf.get_string('key_prefix', 'lsso:')

        try:
            session_id = argparser.parameters[2]
        except (IndexError) as e:
            print ascii.style_text(
                ascii.FG_RED,
                "session:revoke requires a session_id to revoke.")
            return False

        session_key = rd_prefix + "session:" + session_id

        session_exists = rdc.exists(session_key)
        if not session_exists:
            print ascii.style_text(
                ascii.FG_RED,
                "No such session: %s" % (session_id))
            return False

        deleted = rdc.delete(session_key)
        if deleted != 1:
            print ascii.style_text(
                ascii.FG_RED,
                "Could not revoke session: %s" % (session_id))
            return False

        print ascii.style_text(
            ascii.FG_GREEN,
            "Revoked session: %s" % (session_id))
