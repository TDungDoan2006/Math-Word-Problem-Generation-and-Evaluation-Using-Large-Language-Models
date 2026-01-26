def extract_json(response_text):
    import re
    import ast
    match = re.search(r'```json(.*?)```', response_text, re.DOTALL)
    if not match:
        return None
    json_like_str = match.group(1).strip()
    try:
        return ast.literal_eval(json_like_str)
    except (ValueError, SyntaxError) as e:
        print(f"Failed to parse dictionary: {e}")
        return None
    

def extract_dollars(response_text):
    import re
    import ast
    match = re.search(r'start\$(.*?)\$end', response_text, re.DOTALL)
    if not match:
        return None
    json_like_str = match.group(1).strip()
    try:
        return ast.literal_eval(json_like_str)
    except (ValueError, SyntaxError) as e:
        print(f"Failed to parse dictionary: {e}")
        return None



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
