import pytest

from infinity_library.policy import (
    CapabilityError,
    check_capability,
    require_capability,
    validate_capability_set,
)


def test_check_capability_granted():
    assert check_capability("network_restricted", {"network_restricted", "db_read"}) is True


def test_check_capability_not_granted():
    assert check_capability("network_external", {"network_restricted"}) is False


def test_require_capability_raises():
    with pytest.raises(CapabilityError):
        require_capability("network_external", {"network_restricted"})


def test_require_capability_passes():
    require_capability("network_restricted", {"network_restricted", "db_read"})


def test_validate_capability_set_filters_unknown():
    result = validate_capability_set({"network_restricted", "unknown_cap_xyz"})
    assert "network_restricted" in result
    assert "unknown_cap_xyz" not in result


def test_validate_capability_set_all_known():
    caps = {"network_restricted", "db_read", "db_write"}
    assert validate_capability_set(caps) == caps
