from typing import Union, Optional
from pathlib import Path
from contextlib import contextmanager
import os
from py4j.java_gateway import JavaGateway, JVMView, CallbackServerParameters
from py4j.protocol import unescape_new_line

neuralogic: Optional[JVMView] = None
gateway: Optional[JavaGateway] = None

std_out = None
std_err = None


def set_java_home(java_home: Union[Path, str]):
    """
    Set java home environment variable

    :param java_home:
    :return:
    """
    os.environ["JAVA_HOME"] = str(java_home)


def set_std_out(out):
    global std_out
    std_out = out


def set_std_err(out):
    global std_err
    std_err = out


def initialize(die_on_exit=True):
    """
    Initialize the gateway for the Java process. Has to be reinitialized if some settings (JAVA_HOME) changes

    :param die_on_exit:
    :return:
    """
    global gateway, neuralogic

    if gateway is not None:
        try:
            gateway.shutdown()
        except Exception:
            pass

    gateway = JavaGateway.launch_gateway(
        classpath=os.environ["CLASSPATH"],
        redirect_stdout=std_out,
        redirect_stderr=std_err,
        die_on_exit=die_on_exit,
        daemonize_redirect=True,
    )

    raw_token = unescape_new_line(gateway.gateway_parameters.auth_token)
    params = CallbackServerParameters(
        eager_load=False,
        auth_token=raw_token,
        daemonize_connections=True,
        daemonize=True,
        port=25333 #todo gusta: the port changes were causing me problems when starting multiple sessions...(ale mozna jsem to poustel blbe?)
    )

    gateway.start_callback_server(params)

    neuralogic = gateway.jvm


def shutdown():
    if gateway is not None:
        gateway.shutdown()


def get_gateway() -> JavaGateway:
    """
    Get the gateway for the Java process

    :return:
    """
    if gateway is None:
        initialize()
    return gateway


def get_neuralogic() -> JVMView:
    """
    Get the jvm view of the Java process

    :return:
    """
    if neuralogic is None:
        initialize()
    return neuralogic


@contextmanager
def neuralogic_jvm():
    if gateway is None:
        initialize()
    yield
    if gateway is not None:
        shutdown()


os.environ["CLASSPATH"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "jar", "NeuraLogic.jar")
