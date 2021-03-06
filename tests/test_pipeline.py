# Test scenarios based on http://gremlindocs.com/

from gremthon import Gremthon
from itertools import groupby
import sys

#Java imports
from com.tinkerpop.blueprints.impls.tg import TinkerGraphFactory
from java.util import ArrayList
from java.lang import Float

graph = TinkerGraphFactory.createTinkerGraph()
g = Gremthon(graph)

youngest = sys.maxsize


def test_both():
    assert set([v.id for v in g.v(4).both()]) == {'1', '5', '3'}
    assert [v.id for v in g.v(4).both('knows')] == ['1']
    assert set([v.id for v in g.v(4).both('knows', 'created')]) == {'1', '5', '3'}
    assert [v.id for v in g.v(4).both(1, 'knows', 'created')] == ['1']


def test_both_e():
    assert set([e.id for e in g.v(4).both_e()]) == {'8', '10', '11'}
    assert [e.id for e in g.v(4).both_e('knows')] == ['8']
    assert set([e.id for e in g.v(4).both_e('knows', 'created')]) == {'8', '10', '11'}
    assert [e.id for e in g.v(4).both_e(1, 'knows', 'created')] == ['8']


def test_both_v():
    assert [v.id for v in g.e(12).in_v()] == ['3']
    assert [v.id for v in g.e(12).out_v()] == ['6']
    assert [v.id for v in g.e(12).both_v()] == ['6', '3']


def test_graph_edge_iterator():
    assert set([e.id for e in g.E]) == {'10', '7', '9', '8', '11', '12'}


def test_get_adjacent_vertices():
    assert [v.id for v in g.v(4).in_()] == ['1']
    assert [v.id for v in g.v(4).in_e().out_v()] == ['1']
    assert set([v.id for v in g.v(3).in_('created')]) == {'1', '4', '6'}
    assert set([v.id for v in g.v(3).in_(2, 'created')]) < {'1', '4', '6'}
    assert set([v.id for v in g.v(3).in_e('created').out_v()]) == {'1', '4', '6'}
    assert set([v.id for v in g.v(3).in_e(2, 'created').out_v()]) < {'1', '4', '6'}


def test_properties():
    assert g.v(3).name == ['lop']
    assert list(g.v(3))[0].name == 'lop'
    assert list(g.v(3))[0]['name'] == 'lop'
    assert list(g.v(3))[0].get_property('name') == 'lop'


def test_labels():
    assert list(g.v(6).out_e())[0].label == 'created'
    assert [e.id for e in g.v(1).out_e().filter(lambda it: it.label == 'created')] == ['9']
    assert [e.id for e in g.v(1).out_e().has('label','created')] == ['9']


def test_has():
    assert g.V.has('name', 'mark').name == []
    assert g.V.has('name', 'marko').name == ['marko']
    assert g.V.has('name', 'mark', predicate=lambda a,b: b in a).name == ['marko']
    assert set([v.id for v in g.V.has('age')]) == {'1', '2', '4', '6'}
    assert set(g.V.has('age', 30, compare_token='gt').age) == {32, 35}
    assert set(g.V.has('age', 30, compare_token='lt').age) == {29, 27}
    assert set(g.V.has('age', 29, compare_token='gte').age) == {29, 32, 35}


def test_has_not():
    assert set(v.id for v in g.V.has_not('lang')) == {'1', '2', '4', '6'}


def test_link_both_in_out():
    #TODO: see why except doesn't seem to be working as expected
    # marko = g.v(1)
    # g.V.except_([marko])
    pass


def test_map():
    assert list(g.v(1).map())[0] == {'age': 29, 'name': 'marko'}
    actual_items = list(g.V.map('id','age'))
    expected_items = [
        {'id': '3', 'age': None},
        {'id': '2', 'age': 27},
        {'id': '1', 'age': 29},
        {'id': '6', 'age': 35},
        {'id': '5', 'age': None},
        {'id': '4', 'age': 32}
    ]
    assert len(actual_items) == len(expected_items)
    for expected_item in expected_items:
        assert expected_item in actual_items
    assert list(g.v(1).map('id','age'))[0] == {'id': '1', 'age': 29}


def test_memoize():
    assert set([v.id for v in g.V.out().out().memoize(1)]) == {'5', '3'}
    assert set([v.id for v in g.V.out().as_('here').out().memoize('here')]) == {'5', '3'}
    m = {}
    g.V.out().out().memoize(1, m)
    # assert [v.id for v in m[list(g.v(4))[0].vertex]] == ['5', '3']


def test_order():
    #TODO: implement tests for order
    pass


def test_path():
    expected_items = [
        ['1', '2'],
        ['1', '4'],
        ['1', '3']
    ]
    actual_items = [[pair[0].id, pair[1].id] for pair in g.v(1).out().path()]
    assert len(actual_items) == len(expected_items)
    for expected_item in expected_items:
        assert expected_item in actual_items

    actual_items = [p for p in g.v(1).out().path(lambda it: it.id)]
    assert len(actual_items) == len(expected_items)
    for expected_item in expected_items:
        assert expected_item in actual_items

    expected_items = [
        ['1', 'vadas'],
        ['1', 'josh'],
        ['1', 'lop']
    ]

    actual_items = [p for p in g.v(1).out().path(lambda it: it.id, lambda it: it.name)]
    assert len(actual_items) == len(expected_items)
    for expected_item in expected_items:
        assert expected_item in actual_items

    expected_items = [
        ['1', '7', '2'],
        ['1', '8', '4'],
        ['1', '9', '3'],
    ]

    actual_items = [[p[0].id, p[1].id, p[2].id] for p in g.v(1).out_e().in_v().path()]
    assert len(actual_items) == len(expected_items)
    for expected_item in expected_items:
        assert expected_item in actual_items


def test_gather_scatter():
    assert set([v.id for v in list(g.v(1).out().gather(lambda it: it[1:]))[0]]) < {'4', '3', '2'}
    assert set([v.id for v in list(g.v(1).out().gather(lambda it: it[1:]).scatter())]) < {'4', '3', '2'}


def test_select():
    assert [[x[0].id, x[1].id] for x in list(g.v(1).as_('x').out('knows').as_('y').select())] == [['1', '2'], ['1', '4']]
    assert [x[0].id for x in list(g.v(1).as_('x').out('knows').as_('y').select(["y"]))] == ['2', '4']
    assert [x[0] for x in list(g.v(1).as_('x').out('knows').as_('y').select(["y"], lambda it: it.name))] == ['vadas', 'josh']


def test_shuffle():
    shuffled_items = list(g.v(1).out().shuffle())
    out_items = list(g.v(1).out())
    assert len(shuffled_items) == len(out_items)
    for item in shuffled_items:
        assert item in out_items


def test_vertex_iteration():
    assert set([v.id for v in g.V]) == {'3', '2', '1', '6', '5', '4'}
    assert [v.id for v in g.vertices("name", "marko")] == ['1']
    assert g.vertices("name", "marko").name == ['marko']


def test_index_filter():
    assert set([v.id for v in g.V[2:4]]) < {'3', '2', '1', '6', '5', '4'}
    assert len([v.id for v in g.V[2:4]]) == 2
    assert set([v.id for v in g.V.out()[:2]]) < {'3', '2', '1', '6', '5', '4'}
    assert len([v.id for v in g.V.out()[:2]]) == 2
    assert set([v.id for v in g.V.out()[4:]]) < {'3', '2', '1', '6', '5', '4'}
    assert len([v.id for v in g.V.out()[4:]]) == 2
    assert [v.id for v in g.V.out()[4]] == ['5']


def test_dedup():
    assert set([v.id for v in g.v(1).out().in_()]) == {'1', '1', '1', '4', '6'}
    assert set([v.id for v in g.v(1).out().in_().dedup()]) == {'1', '4', '6'}


def test_filter():
    assert set([v.name for v in g.V.filter(lambda it: it.age > 29)]) == {'peter', 'josh'}


def test_interval():
    assert set([e.weight for e in g.E.interval("weight", 0.3, 0.9)]) == {0.5, 0.4000000059604645, 0.4000000059604645}


def test_random():
    random_objects = list(g.V.random(0.5))
    all_objects = list(g.V)
    for obj in random_objects:
        assert obj in all_objects


def test_retain():
    x = [g.v(1).next().vertex, g.v(2).next().vertex, g.v(3).next().vertex]
    assert len(x) == 3
    assert set([v.id for v in g.V.retain(x)]) == {'1', '2', '3'}
    assert len(x) == 3

    x = ArrayList()
    items = [v.id for v in list(g.v(1).out().aggregate(x).out().retain(x))]
    assert  items == ['3']
    items = [v.id for v in list(g.V.as_('x').both().both().both().retain('x'))]
    assert len(items) == 6
    expected_ids = ['1', '3', '4']
    items.sort()
    assert [len(list(group)) for key, group in groupby(items)] == [2, 2, 2]


def test_simple_path():
    assert [v.id for v in g.v(1).out().in_().simple_path()] == ['4', '6']


def test_aggregate():
    x = []
    list(g.v(1).out().aggregate(x))
    assert len(x) == 3
    assert set(v.id for v in x) == {'3', '2', '4'}

    x = []
    item = g.v(1).out().aggregate(x).next()
    assert item is not None
    assert item.id in {'3', '2', '4'}
    assert len(x) == 3
    assert set(v.id for v in x) == {'3', '2', '4'}

    items = g.v(1).out().aggregate(x).next(2)
    assert items is not None
    assert len(items) == 2
    assert set([v.id for v in items]) < {'3', '2', '4'}
    assert set(v.id for v in x) == {'3', '2', '4'}

    ids = []
    list(g.v(1).out().aggregate(ids, lambda it: it.id))
    assert set(ids) == {'3', '2', '4'}

    x = []
    assert set(v.id for v in g.v(1).out().aggregate(x).out()) == {'3', '5'}
    assert set([v.id for v in x]) == {'3', '2', '4'}


def test_group_by():
    x = g.V.group_by(lambda it: it.vertex, lambda it: set(it.out())).cap().next()
    expected = {
        g.v(1).next().vertex: [{g.v(3).next().vertex, g.v(2).next().vertex, g.v(4).next().vertex}],
        g.v(2).next().vertex: [set([])],
        g.v(3).next().vertex: [set([])],
        g.v(4).next().vertex: [{g.v(3).next().vertex, g.v(5).next().vertex}],
        g.v(5).next().vertex: [set([])],
        g.v(6).next().vertex: [{g.v(3).next().vertex}]
    }
    assert str(x) == str(expected)

    m = {}
    g.V.group_by(m, lambda it: it.vertex, lambda it: set(it.out())).iterate()
    assert str(m) == str(expected)

    x = g.V.group_by(lambda it: it.vertex, lambda it: it.out(), lambda it: it[0].count()).cap().next()
    expected_counts = {
        g.v(1).next().vertex: 3,
        g.v(2).next().vertex: 0,
        g.v(3).next().vertex: 0,
        g.v(4).next().vertex: 2,
        g.v(5).next().vertex: 0,
        g.v(6).next().vertex: 1
    }
    assert str(x) == str(expected_counts)

    x = g.V.out().group_by(lambda it: it.name, lambda it: it.in_(), lambda it: list(v.name for v in it[0] if v.age > 30)).cap().next()
    expected_names = {u'vadas': [], u'josh': [], u'lop': [u'josh', u'peter'], u'ripple': [u'josh']}
    assert x == expected_names


def test_group_count():
    m = {}
    items = [v.id for v in g.V.out().group_count(m)]
    assert len(items) == 6
    assert set(items) == {'3', '2', '4', '5'}
    assert m == {
        g.v(2).next().vertex: 1L,
        g.v(3).next().vertex: 3L,
        g.v(4).next().vertex: 1L,
        g.v(5).next().vertex: 1L
    }

    m = {}
    items = [v.id for v in g.v(1).out().group_count(m, lambda it: it, lambda it: it.b+1.0).out().group_count(m, lambda it: it, lambda it: it.b+0.5)]
    assert set(items) == {'3', '5'}
    assert m == {
        g.v(2).next().vertex: 1.0,
        g.v(3).next().vertex: 1.5,
        g.v(4).next().vertex: 1.0,
        g.v(5).next().vertex: 0.5
    }


def test_optional():
    assert [v.id for v in g.V.as_('x').out_e('knows').in_v().has('age', 30, 'gt').back('x')] == ['1']
    assert set([v.id for v in g.V.as_('x').out_e('knows').in_v().has('age', 30, 'gt').optional('x')]) == set(['1', '2', '3', '4', '5', '6'])


def test_side_effect():
    global youngest
    def find_youngest(it):
        global youngest
        youngest = it.age if youngest > it.age else youngest

    assert youngest == sys.maxsize
    assert set(g.V.has('age').side_effect(find_youngest).age) == {29, 27, 32, 35}
    assert youngest == 27


def test_store():
    x = []
    assert g.v(1).out().store(x).next().id in {'3', '2', '4'}
    assert x[0].id in {'3', '2', '4'}


def test_if_then_else():
    assert set(g.V.if_then_else(lambda x: x.id == '1', lambda x: x.getProperty("age"),
                                lambda x: x.getProperty("name"))) == {'vadas', 'josh', 'lop', 'ripple', 'peter', 29}


def test_loop():
    assert set([v.id for v in g.v(1).out().loop(1, lambda x: x.loops < 3)]) == {'3', '5'}
    # assert set([v.id for v in g.v(1).out().as_("x").loop("x", lambda x: x.loops < 3)]) == {'3', '5'}
    assert set([v.id for v in g.v(1).out().loop(1, lambda x: x.loops < 3, lambda x: x.object.id == '3')]) == {'3'}
    # assert set([v.id for v in g.v(1).out().as_("x").loop("x", lambda x: x.loops < 3,
    #                                                      lambda x: x.object.id == '3')]) == {'3'}


def test_keys():
    assert set(g.v(1).next().keys()) == {'name', 'age'}


def test_values():
    assert set(g.v(1).next().values()) == {'marko', 29}


def test_remove():
    assert set(g.E.weight) == {0.4000000059604645, 0.5, 1.0, 0.20000000298023224}
    g.E.has("weight",Float(0.5), 'lt').remove()
    assert set(g.E.weight) == {0.5, 1.0}
    assert len(g.E.weight) == 3


def test_fill():
    m = []
    assert set([v.id for v in g.v(1).out().fill(m)]) == {'2', '4'}
    assert set([v.id for v in m]) == {'2', '4'}


