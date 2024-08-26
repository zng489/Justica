from health.backends import BaseHealthCheckBackend, NotConfiguredService


def get_backends():
    klasses = dict()
    for klass in BaseHealthCheckBackend.__subclasses__():
        if klass.__module__.startswith("health.backends"):
            klasses[klass.name()] = klass

    return klasses


def run_checks(service_name=None):
    backends = get_backends()
    names = backends.keys() if service_name is None else [service_name]
    report = dict()
    for name in names:
        checker = backends[name]()
        try:
            checker.run_check()
            status = "ok" if len(checker.errors) == 0 else "nok"
        except NotConfiguredService:
            status = "not-configured"
        report[name] = {"status": status}

    return report
