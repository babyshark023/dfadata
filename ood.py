"""
Generate out-of-distribution (OOD) DFA test sets with the SAME generator logic and record schema
as the main dataset (Appendix A), but outside the training range:

  ood_len_13_20    : 3-8 states (as in training), input length 13-20   (training: 0-12)
  ood_len_21_30    : 3-8 states (as in training), input length 21-30
  ood_states_9_12  : 9-12 states (training: 3-8), input length 0-12

Every automaton is checked to be different from all training / main-test automata
(same signature definition as the original generator).

Usage:   python make_ood_data.py            (reads data/train.jsonl and data/test.jsonl)
Output:  data_ood/ood_len_13_20.jsonl, data_ood/ood_len_21_30.jsonl, data_ood/ood_states_9_12.jsonl
"""
import argparse, json, random
from pathlib import Path

ALPHABET = ("0", "1")


def generate_random_dfa(num_states):
    states = tuple(range(num_states))
    transitions = {(q, s): random.choice(states) for q in states for s in ALPHABET}
    final_states = set(random.sample(states, random.randint(1, num_states)))
    return transitions, 0, final_states


def run_dfa(input_string, transitions, start_state, final_states):
    cur, steps = start_state, []
    for s in input_string:
        nxt = transitions[(cur, s)]
        steps.append(f"q{cur} --{s}--> q{nxt}")
        cur = nxt
    return cur, ("ACCEPTED" if cur in final_states else "REJECTED"), steps


def transition_table(transitions, states):
    return [{"from": f"q{q}", "symbol": s, "to": f"q{transitions[(q, s)]}"} for q in states for s in ALPHABET]


def dfa_signature(transitions, states, start_state, final_states):
    targets = tuple(transitions[(q, s)] for q in states for s in ALPHABET)
    return (len(states), targets, start_state, tuple(sorted(final_states)))


def signature_from_record(r):
    n = len(r["states"])
    targets = tuple(int(t["to"][1:]) for t in r["transition_table"])
    return (n, targets, int(r["start_state"][1:]), tuple(sorted(int(q[1:]) for q in r["final_states"])))


def make_example(example_id, transitions, states, start_state, final_states, len_lo, len_hi):
    inp = "".join(random.choice(ALPHABET) for _ in range(random.randint(len_lo, len_hi)))
    final_state, result, steps = run_dfa(inp, transitions, start_state, final_states)
    return {
        "id": example_id,
        "states": [f"q{q}" for q in states],
        "alphabet": list(ALPHABET),
        "transition_table": transition_table(transitions, states),
        "start_state": f"q{start_state}",
        "final_states": [f"q{q}" for q in sorted(final_states)],
        "input": inp,
        "steps": steps,
        "final_state": f"q{final_state}",
        "result": result,
    }


def build(name, amount, st_lo, st_hi, len_lo, len_hi, seen, out_dir):
    records = []
    while len(records) < amount:
        states = tuple(range(random.randint(st_lo, st_hi)))
        transitions, start, finals = generate_random_dfa(len(states))
        sig = dfa_signature(transitions, states, start, finals)
        if sig in seen:
            continue
        seen.add(sig)
        records.append(make_example(len(records) + 1, transitions, states, start, finals, len_lo, len_hi))
    path = out_dir / f"{name}.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    acc = sum(r["result"] == "ACCEPTED" for r in records) / len(records)
    print(f"{name}: {len(records)} records, ACCEPTED share {100 * acc:.1f}% -> {path}")
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="data/train.jsonl")
    ap.add_argument("--test", default="data/test.jsonl")
    ap.add_argument("--n", type=int, default=300, help="records per OOD set")
    ap.add_argument("--seed", type=int, default=2025)
    ap.add_argument("--out", default="data_ood")
    a = ap.parse_args()

    random.seed(a.seed)
    seen = set()
    for p in (a.train, a.test):
        for line in Path(p).read_text(encoding="utf-8").splitlines():
            if line.strip():
                seen.add(signature_from_record(json.loads(line)))
    print(f"{len(seen)} automata in train+test will be excluded")
    out = Path(a.out); out.mkdir(exist_ok=True)
    build("ood_len_13_20", a.n, 3, 8, 13, 20, seen, out)
    build("ood_len_21_30", a.n, 3, 8, 21, 30, seen, out)
    build("ood_states_9_12", a.n, 9, 12, 0, 12, seen, out)


if __name__ == "__main__":
    main()