from models import Zone

def load_zones(cfg):
    zones = {}
    for z in cfg["zones"]:
        zones[z["id"]] = Zone(
            id=z["id"],
            label=z["label"],
            topic=z["topic"],
            entry_delay_home=z.get("entry_delay_home", False),
            entry_delay_away=z.get("entry_delay_away", False),
        )
    return zones