# Lending Policy Assistant: RAG with hybrid search, citations and evals

A question-answering assistant for a lender's internal policy documents (eligibility, products,
disbursement, fees, KYC, collections). It answers **only** from the policies, cites the exact
section it used, and refuses when the policies don't cover the question. Everything runs locally
and for free with [Ollama](https://ollama.com); any OpenAI-compatible API can be swapped in.

The emphasis is on **measuring** quality rather than eyeballing it: every design decision below
is backed by numbers from the evaluation suite in [`evals/`](evals/).

> The policy documents are synthetic, written for a fictional lender ("Northwind Credit").

## Architecture

```
                 ┌────────────── ingest (once) ───────────────┐
 data/policies ──► section chunking ──► nomic-embed-text ──► Qdrant (vectors)
   (*.md)                          └──────────────────────► chunks.json (BM25)

 question ──► LLM query rewrite ──► vector search ┐
         └──────────────(original)─► BM25 search  ┴─► Reciprocal Rank Fusion ──► top-4 sections
                                                                                      │
                     answer + [n] citations, or refusal ◄── LLM (evidence-first prompt)
```

| Piece | Choice | Why |
|---|---|---|
| Chunking | one chunk per `##` policy section | a section is one rule and its exceptions; splitting mid-rule loses conditions |
| Embeddings | `nomic-embed-text` via Ollama | free, local, strong on retrieval benchmarks |
| Vector store | Qdrant (embedded on disk; set `QDRANT_URL` for a server) | production-grade, zero setup for development |
| Keyword search | BM25 (`rank-bm25`) | exact terms such as "FOIR", "SMA-1", "penny-drop" |
| Fusion | Reciprocal Rank Fusion | merges ranked lists without calibrating scores |
| Query rewrite | LLM restates the question in policy vocabulary | bridges "close my loan early" ↔ "foreclosure" |
| Generation | evidence-first prompt: quote, then answer | small models refuse less and cite better |
| API | FastAPI `/ask`, `/health` + a minimal web UI | |

No LangChain or LlamaIndex on purpose: each step is a few lines of plain Python, so it is easy to
see and test exactly what happens. The code is about 400 lines in [`src/lendrag/`](src/lendrag/).

## Results

Evaluation set: 34 answerable questions written in everyday customer language, each labelled with
the exact policy section that answers it, plus 6 out-of-scope questions (home loans, crypto, the CEO...)
that must be refused. Full per-question reports: [3B](evals/results-qwen2.5-3b.md), [7B](evals/results-qwen2.5-7b.md).

**Retrieval** (section hit@4 = the exact answering section is among the 4 retrieved; MRR = mean 1/rank)

| Retrieval mode | Section hit@4 | MRR |
|---|---|---|
| BM25 only | 94% | 0.82 |
| Vector only | 97% | 0.89 |
| Hybrid (BM25 + vector, RRF) | 94% | 0.89 |
| Hybrid + query rewrite by `qwen2.5:3b` | 94% | 0.89 |
| **Hybrid + query rewrite by `qwen2.5:7b`** | **100%** | **0.96** |

**End-to-end answers** (hybrid + rewrite, run locally on a laptop RTX 3050 with 4 GB)

| Chat model | Answer accuracy | Cites the right section | False refusals | Out-of-scope refused | Median latency |
|---|---|---|---|---|---|
| `qwen2.5:3b` | 82% (28/34) | 82% | 3/34 | 6/6 | 13.7 s |
| **`qwen2.5:7b`** | **100% (34/34)** | **100%** | **0/34** | **6/6** | 26.5 s |

### What I learned building it

1. **Measure at the right granularity.** My first metric only checked that the right *document*
   was retrieved, and every mode scored about 100%. Labelling the exact *section* showed that hybrid
   search was missing questions like "Can I close my loan early?", because the policy says
   "foreclosure" and BM25 has no word overlap to work with.
2. **Tuning fusion weights didn't fix a vocabulary gap.** A sweep over BM25 weights and top-k never
   brought the foreclosure section into the top 5, so I removed that complexity instead of keeping a
   tuned constant.
3. **Query rewriting works only with a capable model.** The 7B model rewrites "close my loan early"
   as "terms for prepaying the loan", which fixes retrieval. The 3B model rewrites it as "early payoff
   guidelines", which doesn't help and adds latency.
4. **Small models over-refuse.** With a plain "answer only from the excerpts" prompt, the 3B model
   refused answerable questions. Asking it to first copy the supporting evidence and then answer
   reduced false refusals without making it answer out-of-scope questions.
5. **Don't tune the prompt to the test set.** One prompt version listed synonyms taken from my own
   eval questions ("markup loan" = supplier financing). It helped the scores but was test-set leakage,
   so I removed it.
6. **Read the failures, because sometimes the grader is wrong.** Two 7B "failures" were correct
   answers phrased differently ("reviewed manually" vs "manual review"; "after 91 days" vs "more than
   90 days"). I widened those two grading rules after inspecting the answers. The 100% score is after
   that fix, on a small synthetic set: it shows the pipeline works, not that it is perfect.

**Trade-off:** on this 4 GB GPU the 7B model partly runs on the CPU, so answers take about 25 s.
For production, the same code can call a hosted model (`LLM_PROVIDER=openai`), which would bring
latency to 1–2 s. On a small local GPU, `CHAT_MODEL=qwen2.5:3b RETRIEVAL_MODE=hybrid` is the faster
option, at lower accuracy.

## Run it

Prerequisites: Python 3.11+, [uv](https://docs.astral.sh/uv/), [Ollama](https://ollama.com).

```bash
ollama pull nomic-embed-text
ollama pull qwen2.5:7b            # default chat model; see the trade-off above for qwen2.5:3b

uv sync
uv run lendrag-ingest             # builds the index in ./storage
uv run uvicorn lendrag.api:app    # open http://localhost:8000
```

```bash
curl -X POST localhost:8000/ask -H "Content-Type: application/json" \
     -d '{"question": "What happens if my loan disbursement fails?"}'
```

Evaluate and test:

```bash
uv run python evals/run_eval.py              # retrieval ablation + answer quality -> evals/results.md
CHAT_MODEL=qwen2.5:3b uv run python evals/run_eval.py --out results-qwen2.5-3b.md
uv run python evals/run_eval.py --skip-llm   # retrieval only, fast
uv run pytest
```

All settings are environment variables; see [`.env.example`](.env.example). To use a hosted model,
set `LLM_PROVIDER=openai`, `OPENAI_BASE_URL`, `OPENAI_API_KEY` and `CHAT_MODEL`.

## Project layout

```
data/policies/        synthetic policy documents (markdown)
src/lendrag/
  chunking.py         markdown -> section chunks
  ingest.py           chunk -> embed -> Qdrant + chunks.json
  retrieval.py        BM25, vector search, query rewrite, RRF fusion
  rag.py              prompt, evidence/answer parsing, citations, refusals
  llm.py              HTTP clients for Ollama / OpenAI-compatible APIs
  api.py, static/     FastAPI service and web UI
evals/
  questions.jsonl     34 answerable questions (labelled with the exact policy section) + 6 out-of-scope
  run_eval.py         metrics and report
tests/                unit tests (no LLM needed; run in CI)
```

## Next steps

- LLM-as-judge scoring for faithfulness, in addition to the fact-match metric
- A cross-encoder reranker on the fused candidates
- Streaming responses and conversation memory
- Docker Compose with Qdrant and Ollama services
