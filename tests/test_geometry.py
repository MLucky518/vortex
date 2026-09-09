from geometry import square_corners


def test_returns_five_points_closing_the_loop():
    corners = square_corners(5.0, 3.0)
    assert len(corners) == 5
    assert corners[0] == corners[-1]


def test_altitude_is_negative_in_ned():
    for north, east, down in square_corners(5.0, 3.0):
        assert down == -3.0


def test_side_length_is_respected():
    corners = square_corners(5.0, 3.0)
    assert corners[1][0] == 5.0
    assert corners[2][1] == 5.0