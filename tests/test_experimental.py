import pytest

from opinet.experimental import OpinetExperimentalClient


def test_experimental_client_is_explicitly_unimplemented():
    with pytest.raises(NotImplementedError, match="Experimental endpoints"):
        OpinetExperimentalClient()
