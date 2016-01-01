lssoctl
=======

lssoctl is a command line utility for managing lsso.

Note: This project is in its infancy and will probably be going through lots of changes.

Features:
- Uses nice things from [malibu](https://github.com/maiome-development/malibu) so things should remain tested and consistent.
- ...?


Requirements
============

- Python (at least 2.7)
- redis-py
- malibu (>=0.1.5.post3)


Installation
============

- `pip install -e https://github.com/maiome-development/lssoctl.git` or (eventually) `pip install lssoctl`
- ????
- Profit!


Usage
=====

- Coming soon!


Roadmap
=======

- [ ] Auth and session log management
  - [X] `log:view` - Show individual or all logs in pretty printed JSON
  - [ ] `log:delete` - Delete individual or ranges of logs
  - [ ] `log:clear` - Clear an entire log
- [ ] Session management
  - [ ] `session:list` - Show active sessions in the Redis
  - [ ] `session:kill` - Kill a session by ID
  - [ ] `session:info` - View all info for a session, including checkins
- [ ] Token management
  - Requires backend support
  - Tokens used for API access, HTTP basic auth, etc. (differ from access tokens?)
- [ ] Status information
  - `status:get` - Simply displays status of LSSO, SSO backend (`/_health` or `/_ping`), Redis


Contributing
============

Pull requests and issues are more than welcome! I need as much feedback as possible to continue improving the SSO project as a whole.

To discuss code, PRs, issues, or anything else, you can find us on IRC at irc.maio.me in #dev.


Licensing
=========

This project is licensed under the MIT License. You can view the full terms of the license in `/LICENSE.txt`.
