import json
import os


def load_cu_metadata():
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(basedir, "cu_metadata.json")
    with open(path, "r") as f:
        return json.load(f)


STAT_ATTRIBUTES = {
    "Attack": {"min": 99999, "max": 0, "sum": 0},
    "Accuracy": {"min": 99999, "max": 0, "sum": 0},
    "Movement Speed": {"min": 99999, "max": 0, "sum": 0},
    "Attack Speed": {"min": 99999, "max": 0, "sum": 0},
    "Defense": {"min": 99999, "max": 0, "sum": 0},
    "Vitality": {"min": 99999, "max": 0, "sum": 0},
    "Resistance": {"min": 99999, "max": 0, "sum": 0},
    "Magic": {"min": 99999, "max": 0, "sum": 0},
}

unicorns_by_sum_of_stats = {}


def run():
    metadata = load_cu_metadata()
    adult_unicorns_count = 0
    mythic = {}
    for unicorn in metadata:
        try:
            if unicorn["attributes"]["Lifecycle"] == "Adult":
                adult_unicorns_count += 1

                mythic[unicorn["attributes"].get("Mythic", "Common")] = (
                    mythic.get(unicorn["attributes"].get("Mythic", "Common"), 0) + 1
                )
                stats_sum = 0
                for stat_attribute in STAT_ATTRIBUTES.keys():
                    stats_sum += unicorn["attributes"][stat_attribute]

                    STAT_ATTRIBUTES[stat_attribute]["sum"] += unicorn["attributes"][
                        stat_attribute
                    ]
                    STAT_ATTRIBUTES[stat_attribute]["min"] = min(
                        STAT_ATTRIBUTES[stat_attribute]["min"],
                        unicorn["attributes"][stat_attribute],
                    )
                    STAT_ATTRIBUTES[stat_attribute]["max"] = max(
                        STAT_ATTRIBUTES[stat_attribute]["max"],
                        unicorn["attributes"][stat_attribute],
                    )
                unicorns_by_sum_of_stats[unicorn["token_id"]] = stats_sum
        except KeyError:
            print(unicorn)
            pass

    print(f"{adult_unicorns_count}/{len(metadata)} adult unicorns")
    for mythic, count in mythic.items():
        print(f"{mythic}: {count}\t{count/adult_unicorns_count*100}%")

    for stat_attribute, stat_value in STAT_ATTRIBUTES.items():
        print(
            f"{stat_attribute}: min:{stat_value['min']}, max{stat_value['max']}, avarage: {stat_value['sum']/adult_unicorns_count}"
        )

    # sort unicorns_by_sum_of_stats by value descending
    sorted_unicorns_by_sum_of_stats = sorted(
        unicorns_by_sum_of_stats.items(), key=lambda kv: kv[1], reverse=True
    )

    print("Top 10 unicorns by stats sum")
    for unicorn_id, stat_sum in sorted_unicorns_by_sum_of_stats[:10]:
        print(f"id: {unicorn_id} -> {stat_sum}")


run()
