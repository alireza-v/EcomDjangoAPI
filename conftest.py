import pkgutil

pytest_plugins = [
    f"fixtures.{modname}" for _, modname, _ in pkgutil.iter_modules(["fixtures"])
]
