from lendrag.rag import parse_citations, split_evidence
from lendrag.retrieval import rrf, tokenize
from lendrag.scoring import contains_facts, normalize, reciprocal_rank


def test_tokenize_keeps_hyphenated_terms_and_drops_stopwords():
    assert tokenize("What is the penny-drop test for SMA-1?") == ["penny-drop", "test", "sma-1"]


def test_rrf_rewards_documents_ranked_well_by_both_lists():
    fused = rrf([["a", "b", "c"], ["b", "c", "a"]])
    assert fused[0][0] == "b"
    assert {doc for doc, _ in fused} == {"a", "b", "c"}


def test_rrf_includes_documents_found_by_only_one_retriever():
    fused = dict(rrf([["a"], ["z"]]))
    assert set(fused) == {"a", "z"}


def test_split_evidence():
    evidence, answer = split_evidence("EVIDENCE: Fee is 2% [1]\nANSWER: You pay 2% [1].")
    assert evidence == "Fee is 2% [1]"
    assert answer == "You pay 2% [1]."
    assert split_evidence("plain answer") == ("", "plain answer")


def test_parse_citations_handles_groups_and_ignores_out_of_range():
    assert parse_citations("Fee is 2% [1]. Late fee [2, 3]. See [9].", n_sources=4) == [1, 2, 3]


def test_normalize_handles_indian_number_format_and_rupee_sign():
    assert normalize("₹15,00,000") == "rs 1500000"


def test_contains_facts_needs_every_group():
    assert contains_facts("Fee is 2%, minimum Rs 1,999.", [["2%"], ["1999"]])
    assert not contains_facts("Fee is 2%.", [["2%"], ["1999"]])
    assert contains_facts("Up to 15 lakh", [["1500000", "15 lakh"]])


def test_reciprocal_rank():
    assert reciprocal_rank(["x", "y", "z"], "y") == 0.5
    assert reciprocal_rank(["x"], "q") == 0.0
