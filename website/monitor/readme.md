# Monitor

Monitor file changes through disk based file logging.

---

The monitor can watch a file or directory for CREATE/UPDATE/DELETE events.
This application should monitor those events through a live process monitoring.

The discovered changes are pushed to a queue, of which are processed by the tool given db rules.

