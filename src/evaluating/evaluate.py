import json
from typing import Any


def evaluator(my_answers_path: str, ref_answers_path: str,
              ks: tuple[int, ...] = (1, 3, 5, 10)) -> None:
    """Read my_answers_path and ref_answers_path to compare it and calculate
    the recall@k. For each recall (1, 3, 5, and 10) it compares the reference
    and the top-k chunks to find the recall@k by calling recall function.
    Print the result."""
    with open(my_answers_path, "r") as f:
        my_file = json.load(f)
    with open(ref_answers_path, "r") as f:
        reference = json.load(f)

    refs = {q["question_id"]: q["sources"] for q in reference["rag_questions"]}

    print(f"Total number of questions: {len(refs)}")
    print("\n🎯 Evaluation Results")
    print("========================================")

    for k in ks:
        scores = []
        for res in my_file["search_results"]:
            # res : question_id, question, retrieved_sources
            ref_sources = refs.get(res["question_id"])
            # ref_sources = all references : file_path, first_c_i, last_c_i
            if not ref_sources:
                continue
            scores.append(recall(res["retrieved_sources"], ref_sources, k))
        print(f"Recall@{k}: {sum(scores) / len(scores):.3f} "
              f"({(sum(scores) / len(scores))*100}%)")


def recall(retrieved: list[dict[str, Any]],
           ref_sources: list[dict[str, Any]], k: int) -> float:
    """Extract the top-k chunks from the k chunks, then for each reference
    check if the filepath match and if there is enough overlap by calling
    matches function. Return match number divided by references number"""
    top_k = retrieved[:k]
    found = 0
    for ref in ref_sources:
        if any(matches(r, ref) for r in top_k):
            found += 1
    return found / len(ref_sources)


def matches(retrieved: dict[str, Any], ref: dict[str, Any],
            threshold: float = 0.05) -> bool:
    """Compare filepaths and return False if it's different. Call IoU function
    to compare the IoU with the threshold. If the IoU is superior or equal
    to the threshol, it returns True."""
    if retrieved["file_path"] != ref["file_path"]:
        return False
    return iou(retrieved, ref) >= threshold


def iou(retrieved: dict[str, Any], ref: dict[str, Any]) -> float:
    """calcul overlap length divided by the length between the smaller
    first character index and the bigger last character index"""
    my_first = int(retrieved["first_character_index"])
    my_last = int(retrieved["last_character_index"])
    ref_first = int(ref["first_character_index"])
    ref_last = int(ref["last_character_index"])

    inter = max(0, min(my_last, ref_last)) - max(my_first, ref_first)
    union = (my_last - my_first) + (ref_last - ref_first) - inter
    return inter / union if union > 0 else 0.0
