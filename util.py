
def five_minute_floorer(t):
    # floors to the closest 5 minutes
    return t.replace(second=0, microsecond=0, minute=(t.minute//5) * 5)
