# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis/
#
# Most of this work is copyright (C) 2013-2020 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.
#
# END HEADER

from hypothesis import given, strategies as st
from hypothesis.internal.conjecture.choicetree import ChoiceTree, prefix_selection_order


def select(*args):
    return prefix_selection_order(args)


def exhaust(f):
    tree = ChoiceTree()

    results = []

    prefix = ()

    while not tree.exhausted:
        prefix = tree.step(
            prefix_selection_order(prefix), lambda chooser: results.append(f(chooser))
        )
    return results


@given(st.lists(st.integers()))
def test_can_enumerate_a_shallow_set(ls):
    results = exhaust(lambda chooser: chooser.choose(ls))

    assert sorted(results) == sorted(ls)


def test_can_enumerate_a_nested_set():
    @exhaust
    def nested(chooser):
        i = chooser.choose(range(10))
        j = chooser.choose(range(10), condition=lambda j: j > i)
        return (i, j)

    assert sorted(nested) == [(i, j) for i in range(10) for j in range(i + 1, 10)]


def test_can_enumerate_empty():
    @exhaust
    def empty(chooser):
        return 1

    assert empty == [1]


def test_all_filtered_child():
    @exhaust
    def all_filtered(chooser):
        chooser.choose(range(10), condition=lambda j: False)

    assert all_filtered == []


def test_skips_over_exhausted_children():

    results = []

    def f(chooser):
        results.append(
            (
                chooser.choose(range(3), condition=lambda x: x > 0),
                chooser.choose(range(2)),
            )
        )

    tree = ChoiceTree()

    tree.step(select(1, 0), f)
    tree.step(select(1, 1), f)
    tree.step(select(0, 0), f)

    assert results == [(1, 0), (1, 1), (2, 0)]


def test_starts_from_the_end():
    def f(chooser):
        chooser.choose(range(3))

    tree = ChoiceTree()
    assert tree.step(select(), f) == (2,)


def test_skips_over_exhausted_subtree():
    def f(chooser):
        chooser.choose(range(10))

    tree = ChoiceTree()
    assert tree.step(select(8), f) == (8,)
    assert tree.step(select(8), f) == (7,)
