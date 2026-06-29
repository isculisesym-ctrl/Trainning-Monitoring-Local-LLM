import pytest

from src.utils import cosine_similarity, generate_id, hash_text, simple_embedding


def test_embedding_dimension_is_128():
    assert len(simple_embedding("anything at all")) == 128


def test_embedding_identical_prompts_are_maximally_similar():
    a = simple_embedding("write a sorting function")
    b = simple_embedding("write a sorting function")
    assert cosine_similarity(a, b) == pytest.approx(1.0)


def test_embedding_distinguishes_unrelated_words():
    """Regression: the old frequency-shape embedding gave apple==zebra sim=1.0."""
    sim = cosine_similarity(simple_embedding("apple"), simple_embedding("zebra"))
    assert sim < 0.2


def test_embedding_is_order_invariant():
    a = simple_embedding("alpha beta gamma")
    b = simple_embedding("gamma alpha beta")
    assert cosine_similarity(a, b) == pytest.approx(1.0)


def test_cosine_similarity_handles_zero_vector():
    assert cosine_similarity([0.0] * 4, [1.0, 2.0, 3.0, 4.0]) == 0.0


def test_cosine_similarity_handles_length_mismatch():
    assert cosine_similarity([1.0, 2.0], [1.0, 2.0, 3.0]) == 0.0


def test_hash_text_is_sha256_hex():
    digest = hash_text("hello")
    assert len(digest) == 64
    assert digest == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_generate_id_format():
    gid = generate_id()
    assert gid.startswith("gen-")
    assert len(gid) == len("gen-") + 8
