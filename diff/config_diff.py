import json
import copy


class ConfigDiffer:
    def __init__(self, original_path, patched_path):
        with open(original_path, "r", encoding="utf-8") as f:
            self.original = json.load(f)
        with open(patched_path, "r", encoding="utf-8") as f:
            self.patched = json.load(f)

    def generate_delta(self, out_path):
        additions = {}
        deletions = {}
        updates = {}

        for key in self.original:
            if key not in self.patched:
                deletions[key] = self.original[key]
            elif self.original[key] != self.patched[key]:
                updates[key] = {
                    "old": self.original[key],
                    "new": self.patched[key]
                }

        for key in self.patched:
            if key not in self.original:
                additions[key] = self.patched[key]

        delta = {
            "additions": additions,
            "deletions": deletions,
            "updates": updates
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(delta, f, indent=4)

        return delta

    def apply_delta(self, delta, out_path):
        result = copy.deepcopy(self.original)

        for key in delta["deletions"]:
            result.pop(key, None)

        for key, val in delta["updates"].items():
            result[key] = val["new"]

        for key, val in delta["additions"].items():
            result[key] = val

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)
