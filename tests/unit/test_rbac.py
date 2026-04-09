from app.governance.rbac import can_access_zone


def test_data_reader_can_read_consumption():
    assert can_access_zone("data_reader", "consumption", "read") is True


def test_data_reader_cannot_write_raw():
    assert can_access_zone("data_reader", "raw", "write") is False
