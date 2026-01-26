def get_next_question_id(pair_id, counter_path = "question_id_counter.json"):
    import json
    import os

    if os.path.exists(counter_path):
        with open(counter_path, "r") as f:
            counters = json.load(f)
    else:
        counters = {}

    current = counters.get(pair_id, 0) + 1
    question_id = f"{pair_id}_{current:02d}"

    counters[pair_id] = current
    with open(counter_path, "w") as f:
        json.dump(counters, f)

    return question_id
