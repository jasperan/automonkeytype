"""Tests for keyboard layout modeling."""

from automonkeytype.keyboard import (
    LAYOUT,
    QWERTY_NEIGHBORS,
    hand_alternation,
    key_distance,
    same_finger,
    same_hand,
)


def test_layout_has_all_letters():
    for c in "abcdefghijklmnopqrstuvwxyz":
        assert c in LAYOUT, f"Missing key: {c}"


def test_layout_has_space():
    assert " " in LAYOUT


def test_key_distance_self_is_zero():
    assert key_distance("a", "a") == 0.0


def test_key_distance_symmetric():
    assert key_distance("a", "l") == key_distance("l", "a")


def test_key_distance_adjacent_small():
    # Adjacent keys should have small distance
    d = key_distance("f", "g")
    assert 0.5 < d < 2.0, f"Adjacent key distance unexpected: {d}"


def test_key_distance_far_keys_large():
    # Keys far apart should have large distance
    d = key_distance("q", "/")
    assert d > 5.0, f"Far key distance too small: {d}"


def test_key_distance_unknown_key_returns_default():
    d = key_distance("a", "@")
    assert d == 1.5


def test_same_finger_ed():
    # e and d are both middle finger left hand
    assert same_finger("e", "d") is True


def test_same_finger_different():
    # a (left pinky) and s (left ring) are different fingers
    assert same_finger("a", "s") is False


def test_same_hand_left():
    assert same_hand("a", "s") is True
    assert same_hand("q", "t") is True


def test_same_hand_different():
    assert same_hand("a", "j") is False


def test_hand_alternation():
    assert hand_alternation("a", "j") is True
    assert hand_alternation("f", "j") is True
    assert hand_alternation("a", "s") is False


def test_neighbors_exist_for_common_keys():
    for c in "asdfghjkl":
        assert c in QWERTY_NEIGHBORS
        assert len(QWERTY_NEIGHBORS[c]) >= 2


def test_neighbors_are_lowercase():
    for key, neighbors in QWERTY_NEIGHBORS.items():
        assert key == key.lower()
        for n in neighbors:
            assert n == n.lower()
