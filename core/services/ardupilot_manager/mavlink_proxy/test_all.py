import pathlib
import re
import sys
import warnings

import pytest

# import local library
sys.path.append(str(pathlib.Path(__file__).absolute().parent.parent))

from mavlink_proxy.AbstractRouter import AbstractRouter
from mavlink_proxy.Endpoint import Endpoint, EndpointType
from mavlink_proxy.MAVLinkRouter import MAVLinkRouter
from mavlink_proxy.MAVProxy import MAVProxy


def test_endpoint() -> None:
    endpoint = Endpoint("udpout", "0.0.0.0", 14550)
    assert endpoint.connection_type == EndpointType.UDPClient, "Connection type does not match."
    assert endpoint.place == "0.0.0.0", "Connection place does not match."
    assert endpoint.argument == 14550, "Connection argument does not match."
    assert endpoint.__str__() == "udpout:0.0.0.0:14550", "Connection string does not match."
    assert endpoint.asdict() == {
        "connection_type": "udpout",
        "place": "0.0.0.0",
        "argument": 14550,
    }, "Endpoint dict does not match."


def test_endpoint_validators() -> None:
    Endpoint.is_mavlink_endpoint({"connection_type": "tcpin", "place": "0.0.0.0", "argument": 14550})
    Endpoint.is_mavlink_endpoint({"connection_type": "tcpout", "place": "0.0.0.0", "argument": 14550})
    Endpoint.is_mavlink_endpoint({"connection_type": "udpin", "place": "0.0.0.0", "argument": 14550})
    Endpoint.is_mavlink_endpoint({"connection_type": "udpout", "place": "0.0.0.0", "argument": 14550})
    Endpoint.is_mavlink_endpoint({"connection_type": "serial", "place": "/dev/autopilot", "argument": 115200})
    Endpoint.is_mavlink_endpoint({"connection_type": "file", "place": "mavlink_dump"})
    with pytest.raises(ValueError):
        Endpoint.is_mavlink_endpoint({"connection_type": "udpin", "place": "0.0.0.0", "argument": -30})
    with pytest.raises(ValueError):
        Endpoint.is_mavlink_endpoint({"connection_type": "udpin", "place": "42", "argument": 14555})
    with pytest.raises(ValueError):
        Endpoint.is_mavlink_endpoint({"connection_type": "serial", "place": "dev/autopilot", "argument": 115200})
    with pytest.raises(ValueError):
        Endpoint.is_mavlink_endpoint({"connection_type": "serial", "place": "/dev/autopilot", "argument": 100000})
    with pytest.raises(ValueError):
        Endpoint.is_mavlink_endpoint({"connection_type": "file", "place": "mavlink_dump", "argument": 10})
    with pytest.raises(ValueError):
        Endpoint.is_mavlink_endpoint({"connection_type": "file", "place": "/path/to/file"})
    with pytest.raises(ValueError):
        Endpoint.is_mavlink_endpoint({"connection_type": "potato", "place": "path/to/file", "argument": 100})


def test_mavproxy() -> None:
    if not MAVProxy.is_ok():
        warnings.warn("Failed to test mavproxy service", UserWarning)
        return

    assert AbstractRouter.get_interface("MAVProxy"), "Failed to find interface MAVProxy"

    mavproxy = MAVProxy()
    assert mavproxy.name() == "MAVProxy", "Name does not match."
    assert mavproxy.logdir().exists(), "Default MAVProxy log directory does not exist."
    assert mavproxy.set_logdir(pathlib.Path(".")), "Local path as MAVProxy log directory failed."
    assert re.search(r"\d+.\d+.\d+", str(mavproxy.version())) is not None, "Version does not follow pattern."

    endpoint_1 = Endpoint("udpin", "0.0.0.0", 14551)
    endpoint_2 = Endpoint("udpout", "0.0.0.0", 14552)
    endpoint_3 = Endpoint("tcpin", "0.0.0.0", 14553)
    endpoint_4 = Endpoint("tcpout", "0.0.0.0", 14554)
    endpoint_5 = Endpoint("serial", "/dev/radiolink", 57600)
    assert mavproxy.add_endpoint(endpoint_1), "Failed to add first endpoint"
    assert mavproxy.add_endpoint(endpoint_2), "Failed to add second endpoint"
    assert mavproxy.add_endpoint(endpoint_3), "Failed to add third endpoint"
    assert mavproxy.add_endpoint(endpoint_4), "Failed to add fourth endpoint"
    assert mavproxy.add_endpoint(endpoint_5), "Failed to add fifth endpoint"
    assert mavproxy.endpoints() == [
        endpoint_1,
        endpoint_2,
        endpoint_3,
        endpoint_4,
        endpoint_5,
    ], "Endpoint list does not match."

    assert mavproxy.start(Endpoint("udpin", "0.0.0.0", 14550)), "Failed to start mavproxy"
    assert mavproxy.is_running(), "MAVProxy is not running after start."
    assert mavproxy.exit(), "MAVProxy could not stop."
    assert mavproxy.start(Endpoint("udpout", "0.0.0.0", 14550)), "Failed to start mavproxy"
    assert mavproxy.is_running(), "MAVProxy is not running after start."
    assert mavproxy.exit(), "MAVProxy could not stop."
    assert mavproxy.start(Endpoint("tcpin", "0.0.0.0", 14550)), "Failed to start mavproxy"
    assert mavproxy.is_running(), "MAVProxy is not running after start."
    assert mavproxy.exit(), "MAVProxy could not stop."
    assert mavproxy.start(Endpoint("tcpout", "0.0.0.0", 14550)), "Failed to start mavproxy"
    assert mavproxy.is_running(), "MAVProxy is not running after start."
    assert mavproxy.exit(), "MAVProxy could not stop."
    assert mavproxy.start(Endpoint("serial", "/dev/autopilot", 115200)), "Failed to start mavproxy"
    assert mavproxy.is_running(), "MAVProxy is not running after start."
    assert mavproxy.exit(), "MAVProxy could not stop."


def test_mavlink_router() -> None:
    if not MAVLinkRouter.is_ok():
        warnings.warn("Failed to test MAVLinkRouter service", UserWarning)
        return

    assert AbstractRouter.get_interface("MAVLinkRouter"), "Failed to find interface MAVLinkRouter"

    mavlink_router = MAVLinkRouter()
    assert mavlink_router.name() == "MAVLinkRouter", "Name does not match."
    assert mavlink_router.logdir().exists(), "Default MAVLinkRouter log directory does not exist."
    assert mavlink_router.set_logdir(pathlib.Path(".")), "Local path as MAVLinkRouter log directory failed."
    assert re.search(r"\d+", str(mavlink_router.version())) is not None, "Version does not follow pattern."

    endpoint_1 = Endpoint("udpout", "0.0.0.0", 14551)
    endpoint_2 = Endpoint("tcpin", "0.0.0.0", 14552)
    endpoint_3 = Endpoint("tcpout", "0.0.0.0", 14553)
    assert mavlink_router.add_endpoint(endpoint_1), "Failed to add first endpoint"
    assert mavlink_router.add_endpoint(endpoint_2), "Failed to add second endpoint"
    assert mavlink_router.add_endpoint(endpoint_3), "Failed to add third endpoint"
    assert mavlink_router.endpoints() == [
        endpoint_1,
        endpoint_2,
        endpoint_3,
    ], "Endpoint list does not match."
    with pytest.raises(NotImplementedError):
        mavlink_router.add_endpoint(Endpoint("udpin", "0.0.0.0", 14551))
    with pytest.raises(NotImplementedError):
        mavlink_router.add_endpoint(Endpoint("serial", "/dev/autopilot", 115200))

    assert mavlink_router.start(Endpoint("udpin", "0.0.0.0", 14550)), "Failed to start MAVLinkRouter"
    assert mavlink_router.is_running(), "MAVLinkRouter is not running after start."
    assert mavlink_router.exit(), "MAVLinkRouter could not stop."
    assert mavlink_router.start(Endpoint("serial", "/dev/autopilot", 115200)), "Failed to start MAVLinkRouter"
    assert mavlink_router.is_running(), "MAVLinkRouter is not running after start."
    assert mavlink_router.exit(), "MAVLinkRouter could not stop."
    with pytest.raises(NotImplementedError):
        mavlink_router.start(Endpoint("udpout", "0.0.0.0", 14550))
    with pytest.raises(NotImplementedError):
        mavlink_router.start(Endpoint("tcpout", "0.0.0.0", 14550))
