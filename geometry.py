"""Pure geometry. No MAVLink, no async, no hardware. Just math. This file has 
no clue about what its calculations are being used for. It just does the math.
"""


def square_corners(side, altitude):
    """Return (north, east, down) tuples for a square flight path.

    NED coordinates: down is positive, so altitude is negative.
    Starts and ends at the origin.
    """
    down = -altitude
    return [
        (0.0, 0.0, down),
        (side, 0.0, down),
        (side, side, down),
        (0.0, side, down),
        (0.0, 0.0, down),
    ]