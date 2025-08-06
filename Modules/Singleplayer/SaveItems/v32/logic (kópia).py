import sqlite3
import time
import math
import configparser
import os
import json
from datetime import datetime

DB_PATH = "/media/jastronit/Linux1TB/SteamLibrary/steamapps/compatdata/513710/pfx/drive_c/users/steamuser/AppData/Local/SCUM/Saved/SaveFiles/SCUM.db"
SCAN_INTERVAL = 8

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
data_path = os.path.join(base_dir, 'data.ini')
log_path = os.path.join(base_dir, 'log.txt')
config_path = os.path.join(os.path.dirname(__file__), 'config.json')

config_data = configparser.ConfigParser()


# ===== ZÁKLADNÉ ZÁPISOVÉ FUNKCIE =====

def update_data_ini(prisoner_name=None, flagzones_count=None):
    if prisoner_name is not None:
        config_data['prisoner'] = {'name': prisoner_name}
    if flagzones_count is not None:
        config_data['flagzones'] = {'count': str(flagzones_count)}

    try:
        with open(data_path, 'w') as configfile:
            config_data.write(configfile)
    except Exception as e:
        print(f"[LOGIC] Chyba pri zápise do data.ini: {e}")


def log_to_console(message, color=None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    try:
        with open(log_path, 'a') as f:
            f.write(line)
    except Exception as e:
        print(f"[LOGIC] Chyba pri zápise do log.txt: {e}")

# ===== FUNKCIE Z DB =====

def get_user_profile_id(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entity WHERE class = 'FPrisonerEntity';")
    rows = cursor.fetchall()
    for row in rows:
        if row[14] == 0:
            entity_system_id = row[1]
            break
    else:
        return None

    cursor.execute("SELECT * FROM entity_system WHERE id = ?;", (entity_system_id,))
    system_row = cursor.fetchone()
    return system_row[2] if system_row else None


def get_user_name(conn, user_profile_id):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM user_profile WHERE id = ?;", (user_profile_id,))
    row = cursor.fetchone()
    return row[0] if row else None


def get_expiring_items(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT item_entity_id FROM virtualized_item WHERE can_expire = 1;")
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def get_item_positions(conn, item_ids):
    if not item_ids:
        return {}
    placeholders = ','.join(['?'] * len(item_ids))
    query = f"SELECT id, location_x, location_y FROM entity WHERE id IN ({placeholders});"
    cursor = conn.cursor()
    cursor.execute(query, item_ids)
    rows = cursor.fetchall()
    return {row[0]: (row[1], row[2]) for row in rows}


# ===== BASE FUNKCIONALITA =====

def load_or_create_config():
    default_config = {
        "zones": [
            {
                "asset": "/Game/ConZ_Files/BaseBuilding/BaseElements/BP_Base_Flag.BP_Base_Flag_C",
                "radius": 5000,
                "shape": "square"
            },
            {
                "asset": "/Game/ConZ_Files/BaseBuilding/BaseElements/BP_Base_Flag_Supporter.BP_Base_Flag_Supporter_C",
                "radius": 5000,
                "shape": "square"
            }
        ]
    }

    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        return default_config

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log_to_console(f"[LOGIC] Chyba pri načítaní config.json: {e}")
        return default_config


def get_base_positions(conn, user_profile_id):
    config = load_or_create_config()
    asset_rules = {entry["asset"]: entry for entry in config.get("zones", [])}

    cursor = conn.cursor()

    # 1. Získaj všetky base.id, ktoré patria aktuálnemu hráčovi
    cursor.execute("SELECT id FROM base WHERE user_profile_id = ?", (user_profile_id,))
    player_base_ids = set(row[0] for row in cursor.fetchall())

    if not player_base_ids:
        return []

    # 2. Získaj z base_element len tie záznamy, ktoré patria k týmto base.id
    placeholders = ','.join(['?'] * len(player_base_ids))
    query = f"""
        SELECT location_x, location_y, asset
        FROM base_element
        WHERE base_id IN ({placeholders})
    """
    cursor.execute(query, tuple(player_base_ids))
    rows = cursor.fetchall()

    filtered = []
    for x, y, asset in rows:
        if asset not in asset_rules:
            continue

        rule = asset_rules[asset]
        filtered.append({
            "x": x,
            "y": y,
            "asset": asset,
            "radius": rule.get("radius", 5000),
            "shape": rule.get("shape", "square")
        })

    return filtered


def update_can_expire(conn, item_ids):
    if not item_ids:
        return
    placeholders = ','.join(['?'] * len(item_ids))
    query = f"UPDATE virtualized_item SET can_expire = 0 WHERE item_entity_id IN ({placeholders});"
    cursor = conn.cursor()
    cursor.execute(query, item_ids)
    conn.commit()
    log_to_console(f"[Save] {len(item_ids)} Items have been saved!")


# ===== Hlavný LOOP =====

def main_loop(gui=None, stop_event=None):
    while not (stop_event and stop_event.is_set()):
        try:
            with sqlite3.connect(DB_PATH, timeout=1) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA locking_mode=NORMAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                conn.execute("PRAGMA read_uncommitted = true;")

                expiring_ids = get_expiring_items(conn)
                item_positions = get_item_positions(conn, expiring_ids)

                user_profile_id = get_user_profile_id(conn)
                prisoner_name = get_user_name(conn, user_profile_id) if user_profile_id else "N/A"

                base_zones = get_base_positions(conn, user_profile_id)

                items_to_protect = []

                for item_id, (ix, iy) in item_positions.items():
                    for base in base_zones:
                        bx, by = base["x"], base["y"]
                        radius = base["radius"]
                        shape = base["shape"]

                        dx = abs(ix - bx)
                        dy = abs(iy - by)

                        if shape == "square":
                            if dx <= radius and dy <= radius:
                                items_to_protect.append(item_id)
                                break
                        elif shape == "circle":
                            distance = math.sqrt(dx**2 + dy**2)
                            if distance <= radius:
                                items_to_protect.append(item_id)
                                break

                update_can_expire(conn, items_to_protect)
                update_data_ini(prisoner_name=prisoner_name, flagzones_count=len(base_zones))

        except Exception as e:
            log_to_console(f"[CHYBA] {e}")

        if stop_event:
            stop_event.wait(SCAN_INTERVAL)
        else:
            time.sleep(SCAN_INTERVAL)


def logic_main_loop(gui, stop_event):
    try:
        with open(log_path, 'w') as f:
            f.write("[SaveItems] Module Loaded...\n")
    except Exception as e:
        print(f"[LOGIC] Nepodarilo sa vytvoriť log.txt: {e}")

    main_loop(gui, stop_event)


if __name__ == "__main__":
    main_loop()

