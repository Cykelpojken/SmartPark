import pytest  # pragma: no cover

def pytest_addoption(parser):  # pragma: no cover
    parser.addoption(
        "--cmdopt", action="store", default="type1", help="my option: type1 or type2"
    )

@pytest.fixture  # pragma: no cover
def cmdopt(request):  # pragma: no cover
    return request.config.getoption("--cmdopt") 