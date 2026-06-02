from alpha_fox.station.band_edges import check_band_edges


def test_frequency_inside_20m_band_is_allowed() -> None:
    result = check_band_edges(14_074_000)

    assert result.allowed is True
    assert result.band_name == "20m"


def test_frequency_inside_40m_band_is_allowed() -> None:
    result = check_band_edges(7_074_000)

    assert result.allowed is True
    assert result.band_name == "40m"


def test_frequency_outside_supported_bands_is_rejected() -> None:
    result = check_band_edges(70_000_000)

    assert result.allowed is False
    assert result.band_name is None


def test_zero_frequency_is_rejected() -> None:
    result = check_band_edges(0)

    assert result.allowed is False
    assert "greater than zero" in result.message
