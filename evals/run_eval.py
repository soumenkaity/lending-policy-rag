"""Evaluate retrieval and answers against a labelled question set.

    uv run python evals/run_eval.py              # retrieval ablation + answer quality
    uv run python evals/run_eval.py --skip-llm   # retrieval only, no chat model calls (fast)

Metrics
  Retrieval (answerable questions): hit@k = expected document in the top-k chunks; MRR = mean 1/rank.
  Answers: accuracy = every required fact present; citation rate = answer cites at least one source;
  grounded citation = a cited source comes from the expected document; refusal accuracy = out-of-scope
  questions answered with a refusal; false refusals = answerable questions wrongly refused.
"""

import argparse
import json
import statistics
import sys
from pathlib import Path

from lendrag.config import Settings
from lendrag.rag import answer_question
from lendrag.retrieval import Retriever
from lendrag.scoring import contains_facts, reciprocal_rank

HERE = Path(__file__).parent


def pct(x: float) -> str:
    return f"{100 * x:.0f}%"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-llm", action="store_true")
    parser.add_argument("--out", default="results.md", help="file name inside evals/ for the report")
    args = parser.parse_args()

    settings = Settings()
    items = [json.loads(line) for line in (HERE / "questions.jsonl").read_text(encoding="utf-8").splitlines() if line]
    answerable = [q for q in items if q["expected_doc"]]
    out_of_scope = [q for q in items if not q["expected_doc"]]
    k = settings.top_k
    retriever = Retriever(settings)
    lines = [f"# Evaluation results\n", f"Chat model `{settings.chat_model}`, embeddings `{settings.embed_model}`, top-k = {k}. "
             f"{len(answerable)} answerable + {len(out_of_scope)} out-of-scope questions.\n"]

    # 1. Retrieval ablation, scored against the exact policy section that answers each question
    lines += ["## Retrieval\n", f"| Mode | Section hit@{k} | Section MRR | Document hit@{k} | Missed |", "|---|---|---|---|---|"]
    modes = ("bm25", "vector", "hybrid") if args.skip_llm else ("bm25", "vector", "hybrid", "hybrid+rewrite")
    for mode in modes:
        chunk_rrs, doc_hits, missed = [], 0, []
        for q in answerable:
            found = retriever.search(q["question"], k, mode=mode)
            rr = reciprocal_rank([c.id for c in found], q["expected_chunk"])
            chunk_rrs.append(rr)
            doc_hits += q["expected_doc"] in {c.doc for c in found}
            if rr == 0:
                missed.append(q["id"])
        hit = sum(r > 0 for r in chunk_rrs) / len(chunk_rrs)
        mrr = statistics.mean(chunk_rrs)
        lines.append(f"| {mode} | {pct(hit)} | {mrr:.2f} | {pct(doc_hits / len(answerable))} | {', '.join(missed) or '-'} |")
        print(f"retrieval {mode:15s} section-hit@{k}={pct(hit)} MRR={mrr:.2f} missed={missed}")
    lines.append("")

    # 2. End-to-end answers with the configured retrieval mode
    if not args.skip_llm:
        rows, correct, cited, grounded, false_refusals, latencies = [], 0, 0, 0, 0, []
        for q in answerable:
            a = answer_question(q["question"], retriever, settings)
            latencies.append(a.latency_ms)
            ok = a.answered and contains_facts(a.text, q["must_include"])
            correct += ok
            cited += bool(a.cited)
            grounded += any(a.sources[i - 1].id == q["expected_chunk"] for i in a.cited)
            false_refusals += not a.answered
            rows.append((q["id"], q["question"], ok, a.text))
            print(f"{q['id']} {'PASS' if ok else 'FAIL'} {a.latency_ms}ms  {a.text[:110]!r}")
        refused = 0
        for q in out_of_scope:
            a = answer_question(q["question"], retriever, settings)
            latencies.append(a.latency_ms)
            refused += not a.answered
            rows.append((q["id"], q["question"], not a.answered, a.text))
            print(f"{q['id']} {'PASS' if not a.answered else 'FAIL'} {a.latency_ms}ms  {a.text[:110]!r}")

        n = len(answerable)
        lines += [
            f"## Answers (retrieval mode `{settings.retrieval_mode}`)\n",
            "| Metric | Value |", "|---|---|",
            f"| Answer accuracy (required facts present) | {pct(correct / n)} ({correct}/{n}) |",
            f"| Answers with a citation | {pct(cited / n)} |",
            f"| Citation points to the right policy section | {pct(grounded / n)} |",
            f"| False refusals on answerable questions | {false_refusals}/{n} |",
            f"| Refusal accuracy on out-of-scope questions | {pct(refused / len(out_of_scope))} ({refused}/{len(out_of_scope)}) |",
            f"| Median latency | {statistics.median(latencies) / 1000:.1f} s |",
            "",
            "## Per-question results\n",
            "| ID | Question | Pass | Answer |", "|---|---|---|---|",
        ]
        for qid, question, ok, text in rows:
            lines.append(f"| {qid} | {question} | {'✅' if ok else '❌'} | {text.replace('|', '/').replace(chr(10), ' ')} |")

    retriever.close()
    (HERE / args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {HERE / args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
