from alpha_fox.dsp.waterfall_service import MockWaterfallService


def test_mock_waterfall_frame_shape() -> None:
    service = MockWaterfallService(bin_count=512)

    frame = service.get_frame()

    assert frame.center_frequency_hz > 0
    assert frame.sample_rate_hz == 48_000
    assert frame.min_db == -120.0
    assert frame.max_db == -20.0
    assert len(frame.bins) == 512


def test_mock_waterfall_bins_are_numbers() -> None:
    service = MockWaterfallService(bin_count=128)

    frame = service.get_frame()

    assert len(frame.bins) == 128
    assert all(isinstance(value, float) for value in frame.bins)
