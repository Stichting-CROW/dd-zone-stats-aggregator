from string import Template

import notifications.telegram
import re

def send_notifications(state_changes):
    for state_change in state_changes:
        if len(state_change.opened) > 0:
            text = get_open_microhub_text(state_change)
            notifications.telegram.send_msg(text, state_change.stop.municipality)
        if len(state_change.closed) > 0:
            text = get_close_microhub_text(state_change)
            notifications.telegram.send_msg(text, state_change.stop.municipality)

def get_open_microhub_text(state_change):
    open_microhub = Template("""
Microhub *[$name_microhub]($url_microhub)* weer **beschikbaar** \n\n$url_microhub
    """
    )
    stop = state_change.stop
    return open_microhub.substitute(name_microhub = re.escape(stop.name), url_microhub = re.escape("https://dashboarddeelmobiliteit.nl/map/zones/" + stop.geography_id),
        modalities = ','.join(state_change.opened))

def get_close_microhub_text(state_change):
    close_microhub = Template("""
Microhub *[$name_microhub]($url_microhub) VOL* \n\n$url_microhub
    """
    )
    stop = state_change.stop
    return close_microhub.substitute(name_microhub = re.escape(stop.name), url_microhub = re.escape("https://dashboarddeelmobiliteit.nl/map/zones/" + stop.geography_id),
        modalities = ','.join(state_change.closed))
