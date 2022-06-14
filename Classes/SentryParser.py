"""
 Created by Rawa on 06/14/2022 10:00 PM
 For the project: MeshMonitors.io

 We wanted to use Sentry's powerful API to parse the traces and send them to our webhook.

 Note: This is a work in progress.
 I created this class to parse message events, and exceptions from Sentry.
 I'd like to add more features to this class.
 Open a PR if you have any suggestions.
"""

from typing import Any, List, TypeVar, Type, cast, Callable
from datetime import datetime

T = TypeVar("T")


def from_str(obj: Any) -> str | None:
    if isinstance(obj, str):
        return obj
    return None


def from_bool(obj: Any) -> bool | None:
    if isinstance(obj, bool):
        return obj
    return None


def to_class(c: Type[T], obj: Any) -> dict:
    assert isinstance(obj, c)
    if isinstance(obj, dict):
        return cast(Any, obj).to_dict()
    return obj.to_dict()


def from_int(obj: Any) -> int | None:
    if isinstance(obj, int):
        return obj
    return None


def from_list(fold: Callable[[Any], T], obj: Any) -> List[T] | None:
    if isinstance(obj, list):
        return [fold(item) for item in obj]
    return None


def from_none(obj: Any) -> Any:
    # assert obj is None
    return obj


def from_datetime(time: Any) -> datetime:
    if isinstance(time, float):
        timestamp = float(time)
        return datetime.fromtimestamp(timestamp)

    return datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ")


class Mechanism:
    type: str
    handled: bool

    def __init__(self, mechanism_type: str, handled: bool) -> None:
        self.type = mechanism_type
        self.handled = handled

    @staticmethod
    def from_dict(obj: Any) -> Any:
        if isinstance(obj, dict):
            mech_type = from_str(obj.get("type"))
            handled = from_bool(obj.get("handled"))
            return Mechanism(mech_type, handled)
        return None

    def to_dict(self) -> dict:
        result: dict = {"type": from_str(self.type), "handled": from_bool(self.handled)}
        return result


class Annotations:
    pass

    def __init__(self, ) -> None:
        pass

    @staticmethod
    def from_dict(obj: Any) -> Any:
        if isinstance(obj, dict):
            return Annotations()


class VarIdentifier:
    def __init__(self, var_identifier, var_value) -> None:
        self.var_identifier = var_identifier
        self.var_value = var_value


class Vars:

    def __init__(self) -> None:
        pass

    @staticmethod
    def from_dict(obj: Any) -> 'List[VarIdentifier]' or None:
        if isinstance(obj, list):
            vars_list = [VarIdentifier(var_identifier, var_value) for var_identifier, var_value in obj.items()]
            return vars_list
        return None


class Frame:
    filename: str
    abs_path: str
    function: str
    module: str
    lineno: int
    pre_context: list[str]
    context_line: str
    post_context: list[Any]
    vars: list[VarIdentifier]
    in_app: bool

    def __init__(self, filename: str, abs_path: str, function: str, module: str, lineno: int, pre_context: List[str],
                 context_line: str, post_context: List[Any], frame_vars: list[VarIdentifier], in_app: bool) -> None:
        self.filename = filename
        self.abs_path = abs_path
        self.function = function
        self.module = module
        self.lineno = lineno
        self.pre_context = pre_context
        self.context_line = context_line
        self.post_context = post_context
        self.vars = frame_vars
        self.in_app = in_app

    @staticmethod
    def from_dict(obj: Any) -> 'Frame' or None:
        if isinstance(obj, dict):
            filename = from_str(obj.get("filename"))
            abs_path = from_str(obj.get("abs_path"))
            function = from_str(obj.get("function"))
            module = from_str(obj.get("module"))
            lineno = from_int(obj.get("lineno"))
            pre_context = from_list(from_str, obj.get("pre_context"))
            context_line = from_str(obj.get("context_line"))
            post_context = from_list(lambda context: context, obj.get("post_context"))
            frame_vars = Vars.from_dict(obj.get("vars"))
            in_app = from_bool(obj.get("in_app"))
            return Frame(filename, abs_path, function, module, lineno, pre_context, context_line,
                         post_context, frame_vars, in_app)

    def to_dict(self) -> dict:
        result: dict = {"filename": from_str(self.filename), "abs_path": from_str(self.abs_path),
                        "function": from_str(self.function), "module": from_str(self.module),
                        "lineno": from_int(self.lineno), "pre_context": from_list(from_str, self.pre_context),
                        "context_line": from_str(self.context_line),
                        "post_context": from_list(lambda context: context, self.post_context),
                        "vars": to_class(Vars, self.vars),
                        "in_app": from_bool(self.in_app)}
        return result


class Stacktrace:
    frames: List[Frame]

    def __init__(self, frames: List[Frame]) -> None:
        self.frames = frames

    @staticmethod
    def from_dict(obj: Any) -> 'Stacktrace' or None:
        if isinstance(obj, dict):
            frames = from_list(Frame.from_dict, obj.get("frames"))
            return Stacktrace(frames)
        return None

    def to_dict(self) -> dict:
        result: dict = {"frames": from_list(lambda frm: to_class(Frame, frm), self.frames)}
        return result


class Value:
    module: None
    type: str
    value: str
    mechanism: Mechanism
    stacktrace: Stacktrace

    def __init__(self, module: None, trace_type: str, value: str, mechanism: Mechanism, stacktrace: Stacktrace) -> None:
        self.module = module
        self.type = trace_type
        self.value = value
        self.mechanism = mechanism
        self.stacktrace = stacktrace

    @staticmethod
    def from_dict(obj: Any) -> 'Value' or None:
        if isinstance(obj, dict):
            module = from_none(obj.get("module"))
            trace_type = from_str(obj.get("type"))
            value = from_str(obj.get("value"))
            mechanism = Mechanism.from_dict(obj.get("mechanism"))
            stacktrace = Stacktrace.from_dict(obj.get("stacktrace"))
            return Value(module, trace_type, value, mechanism, stacktrace)

    def to_dict(self) -> dict:
        result: dict = {"module": from_none(self.module), "type": from_str(self.type), "value": from_str(self.value),
                        "mechanism": to_class(Mechanism, self.mechanism),
                        "stacktrace": to_class(Stacktrace, self.stacktrace)}
        return result


class Breadcrumbs:
    values: List[Value]

    def __init__(self, values: List[Value]) -> None:
        self.values = values

    @staticmethod
    def from_dict(obj: Any) -> 'Breadcrumbs' or None:
        if isinstance(obj, list):
            values = from_list(Value.from_dict, obj.get("values"))
            return Breadcrumbs(values)

    def to_dict(self) -> dict:
        result: dict = {"values": from_list(lambda bc: to_class(Value, bc), self.values)}
        return result


class Runtime:
    name: str
    version: str
    build: str

    def __init__(self, name: str, version: str, build: str) -> None:
        self.name = name
        self.version = version
        self.build = build

    @staticmethod
    def from_dict(obj: Any) -> 'Runtime' or None:
        if isinstance(obj, dict):
            name = from_str(obj.get("name"))
            version = from_str(obj.get("version"))
            build = from_str(obj.get("build"))
            return Runtime(name, version, build)
        return None

    def to_dict(self) -> dict:
        result: dict = {"name": from_str(self.name), "version": from_str(self.version), "build": from_str(self.build)}
        return result

    def __repr__(self):
        # Just for my use of discord webhooks, change this to whatever you want
        return f"\nName: {self.name}\nVersion{self.version}\nBuild{self.build}"


class Contexts:
    runtime: Runtime

    def __init__(self, runtime: Runtime) -> None:
        self.runtime = runtime

    @staticmethod
    def from_dict(obj: Any) -> 'Contexts' or None:
        if isinstance(obj, dict):
            runtime = Runtime.from_dict(obj.get("runtime"))
            return Contexts(runtime)
        return None

    def to_dict(self) -> dict:
        result: dict = {"runtime": to_class(Runtime, self.runtime)}
        return result

    def __repr__(self):
        return f"""Runtime Information: {self.runtime}"""


class Args:
    def __init__(self, arg: str) -> None:
        self.arg = arg

    def __repr__(self):
        return f"""-> {self.arg}"""


class ExtraCommands:
    def __init__(self, extra_name: str, extra_callers: list[str]) -> None:
        self.extra_name = extra_name
        self.extra_callers = [Args(caller) for caller in extra_callers]

    def __repr__(self):
        return f"""Extra Commands: \nArg: {self.extra_name} {''.join([str(caller) for caller in self.extra_callers])}"""


class Extra:
    def __init__(self):
        pass

    @staticmethod
    def from_dict(obj: Any) -> list[ExtraCommands] or None:
        if isinstance(obj, dict):
            extras = [ExtraCommands(extra_name, extra_callers) for extra_name, extra_callers in obj.items()]
            return extras
        return None


class Module:
    def __init__(self, module, v) -> None:
        self.name = module
        self.version = v

    def to_dict(self) -> dict:
        result: dict = {"name": from_str(self.name), "version": from_str(self.version)}
        return result


class Modules:
    def __init__(self) -> None:
        pass

    @staticmethod
    def from_dict(obj: Any) -> list[Module] or None:
        if isinstance(obj, dict):
            modules = [Module(module, obj[module]) for module in obj]
            return modules
        return None


class Package:
    name: str
    version: str

    def __init__(self, name: str, version: str) -> None:
        self.name = name
        self.version = version

    @staticmethod
    def from_dict(obj: Any) -> 'Package' or None:
        if isinstance(obj, dict):
            name = from_str(obj.get("name"))
            version = from_str(obj.get("version"))
            return Package(name, version)
        return None

    def to_dict(self) -> dict:
        result: dict = {"name": from_str(self.name), "version": from_str(self.version)}
        return result

    def __repr__(self):
        return f"""Package: {self.name} {self.version}"""


class SDK:
    name: str
    version: str
    packages: List[Package]
    integrations: List[str]

    def __init__(self, name: str, version: str, packages: List[Package], integrations: List[str]) -> None:
        self.name = name
        self.version = version
        self.packages = packages
        self.integrations = integrations

    @staticmethod
    def from_dict(obj: Any) -> 'SDK' or None:
        if isinstance(obj, dict):
            name = from_str(obj.get("name"))
            version = from_str(obj.get("version"))
            packages = from_list(Package.from_dict, obj.get("packages"))
            integrations = from_list(from_str, obj.get("integrations"))
            return SDK(name, version, packages, integrations)
        return None

    def to_dict(self) -> dict:
        result: dict = {"name": from_str(self.name), "version": from_str(self.version),
                        "packages": from_list(lambda sdk: to_class(Package, sdk), self.packages),
                        "integrations": from_list(from_str, self.integrations)}
        return result


class ExceptionValue:
    module: None
    type: str
    value: str
    mechanism: Mechanism
    stacktrace: Stacktrace

    def __init__(self, module: None, exec_type: str, value: str, mechanism: Mechanism, stacktrace: Stacktrace) -> None:
        self.module = module
        self.type = exec_type
        self.value = value
        self.mechanism = mechanism
        self.stacktrace = stacktrace

    @staticmethod
    def from_dict(obj: Any) -> 'ExceptionValue' or None:
        if isinstance(obj, dict):
            module = from_none(obj.get("module"))
            exec_type = from_str(obj.get("type"))
            value = from_str(obj.get("value"))
            mechanism = Mechanism.from_dict(obj.get("mechanism"))
            stacktrace = Stacktrace.from_dict(obj.get("stacktrace"))
            return ExceptionValue(module, exec_type, value, mechanism, stacktrace)
        return None

    def to_dict(self) -> dict:
        result: dict = {"module": from_none(self.module), "type": from_str(self.type), "value": from_str(self.value),
                        "mechanism": to_class(Mechanism, self.mechanism),
                        "stacktrace": to_class(Stacktrace, self.stacktrace)}
        return result


class ExceptionClass:
    values: List[ExceptionValue]

    def __init__(self, values: List[ExceptionValue]) -> None:
        self.values = values

    @staticmethod
    def from_dict(obj: Any) -> 'ExceptionClass' or None:
        if isinstance(obj, dict):
            values = from_list(ExceptionValue.from_dict, obj.get("values"))
            return ExceptionClass(values)
        return None

    def to_dict(self) -> dict:
        result: dict = {"values": from_list(lambda x: to_class(ExceptionValue, x), self.values)}
        return result


class SentryTrace:
    message: str
    level: str
    exception: ExceptionClass
    event_id: str
    timestamp: datetime
    breadcrumbs: Breadcrumbs
    contexts: Contexts
    modules: list[Module]
    extra: list[ExtraCommands]
    release: str
    environment: str
    server_name: str
    sdk: SDK
    platform: str

    def __init__(self, message: str, level: str, exception: ExceptionClass, event_id: str, timestamp: datetime,
                 breadcrumbs: Breadcrumbs, contexts: Contexts, modules: list[Module], extra: list[ExtraCommands],
                 release: str, environment: str, server_name: str, sdk: SDK, platform: str) -> None:
        self.message = message
        self.level = level
        self.exception = exception
        self.event_id = event_id
        self.timestamp = timestamp
        self.breadcrumbs = breadcrumbs
        self.contexts = contexts
        self.modules = modules
        self.extra = extra
        self.release = release
        self.environment = environment
        self.server_name = server_name
        self.sdk = sdk
        self.platform = platform

    @staticmethod
    def from_dict(obj: Any) -> 'SentryTrace' or None:
        if isinstance(obj, dict):
            message = from_str(obj.get("message")) if obj.get("message") is not None else None
            level = from_str(obj.get("level")) if obj.get("level") is not None else None
            exception = ExceptionClass.from_dict(obj.get("exception")) if obj.get("exception") is not None else None
            event_id = from_str(obj.get("event_id")) if obj.get("event_id") is not None else None
            timestamp = from_datetime(obj.get("timestamp")) if obj.get("timestamp") is not None else None
            breadcrumbs = Breadcrumbs.from_dict(obj.get("breadcrumbs")) if obj.get("breadcrumbs") is not None else None
            contexts = Contexts.from_dict(obj.get("contexts")) if obj.get("contexts") is not None else None
            modules = Modules.from_dict(obj.get("modules")) if obj.get("modules") is not None else None
            extra = Extra.from_dict(obj.get("extra")) if obj.get("extra") is not None else None
            release = from_str(obj.get("release")) if obj.get("release") is not None else None
            environment = from_str(obj.get("environment")) if obj.get("environment") is not None else None
            server_name = from_str(obj.get("server_name")) if obj.get("server_name") is not None else None
            sdk = SDK.from_dict(obj.get("sdk")) if obj.get("sdk") is not None else None
            platform = from_str(obj.get("platform")) if obj.get("platform") is not None else None
            return SentryTrace(message, level, exception, event_id, timestamp, breadcrumbs,
                               contexts, modules, extra, release, environment, server_name, sdk, platform)
        print("A valid <dict> is required to create a SentryTrace object")
        return None

    def to_dict(self) -> dict:
        result: dict = {"level": from_str(self.level), "exception": to_class(ExceptionClass, self.exception),
                        "event_id": from_str(self.event_id), "timestamp": self.timestamp.isoformat(),
                        "breadcrumbs": to_class(Breadcrumbs, self.breadcrumbs),
                        "contexts": to_class(Contexts, self.contexts), "modules": to_class(Modules, self.modules),
                        "extra": to_class(Extra, self.extra), "release": from_str(self.release),
                        "environment": from_str(self.environment), "server_name": from_str(self.server_name),
                        "sdk": to_class(SDK, self.sdk), "platform": from_str(self.platform)}
        return result


def sentry_trace_from_dict(s: Any) -> SentryTrace:
    return SentryTrace.from_dict(s)


def sentry_trace_to_dict(trace: SentryTrace) -> Any:
    return to_class(SentryTrace, trace)
