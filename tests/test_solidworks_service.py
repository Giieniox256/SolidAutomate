from pathlib import Path

import pytest

from solid_automate.core.solidworks_service import SolidWorksService

part_path = Path(__file__).parent / "test_3d_models" / "sw_tol1.SLDPRT"


@pytest.fixture(scope="session")
def con_sw():
    sw = SolidWorksService()
    sw.connect()
    yield sw
    sw.disconnect()


def test_sw_service_connection():
    """Method test sw_service connection"""
    sw_service = SolidWorksService()
    assert sw_service.connect()


class TestPart:
    def test_open_part(self, con_sw):
        """Method test sw_service open part"""
        sw = con_sw
        assert sw.open_part(str(part_path)), f"Open part not possible"
