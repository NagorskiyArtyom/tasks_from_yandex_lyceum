def calculate_spn(toponym):
    envelope = toponym["boundedBy"]["Envelope"]
    left, bottom = envelope["lowerCorner"].split()
    right, top = envelope["upperCorner"].split()

    delta_lon = abs(float(right) - float(left))
    delta_lat = abs(float(top) - float(bottom))

    return f"{delta_lon},{delta_lat}"
