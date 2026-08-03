import os
import json
from fetch_contributions import fetch_contributions

def test_fetch_contributions():
    test_json = "data/test-contributions.json"
    if os.path.exists(test_json):
        os.remove(test_json)

    data = fetch_contributions("mat-dgruber", test_json)

    assert os.path.exists(test_json), "Output JSON file was not created"
    assert "total_contributions" in data, "total_contributions key missing"
    assert "days" in data, "days key missing"
    assert len(data["days"]) > 0, "days list is empty"
    assert data["username"] == "mat-dgruber", "username mismatch"

    # Verify JSON content matches returned data
    with open(test_json, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["username"] == data["username"]
    assert loaded["total_contributions"] == data["total_contributions"]
    assert len(loaded["days"]) == len(data["days"])

    # Clean up
    os.remove(test_json)
    print("test_fetch_contributions passed successfully.")

if __name__ == "__main__":
    test_fetch_contributions()
