# -*- coding: utf-8 -*-
from vispy.scene.node import Node
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main, raises)
from vispy.visuals.transforms import STTransform
import numpy as np


class EventCheck(object):
    def __init__(self, emitter):
        self._events = []
        self.emitter = emitter
        emitter.connect(self.callback)

    def callback(self, event):
        self._events.append(event)

    @property
    def events(self):
        ev = self._events
        self._events = []
        return ev


@requires_application()
def test_topology():
    c = TestingCanvas()
    assert c.scene.canvas is c
    with raises(AttributeError):
        c.foo = 'bar'

    w = c.central_widget
    assert w.parent is c.scene
    assert w.scene_node is c.scene
    assert w.document_node is c.scene

    g = w.add_grid()
    with raises(AttributeError):
        g.foo = 'bar'

    grid_check = EventCheck(g.events.children_change)

    v1 = g.add_view(row=0, col=0)
    assert v1.parent is g
    assert v1.scene_node is c.scene

    assert len(grid_check.events) == 1

    v2 = g.add_view(row=1, col=0)
    assert v2.parent is g
    assert v2.scene_node is c.scene
    assert v2.document_node is c.scene

    assert len(grid_check.events) == 1

    n1 = Node()
    n1_parent_check = EventCheck(n1.events.parent_change)
    n1_child_check = EventCheck(n1.events.children_change)
    v1.add(n1)
    assert len(n1_parent_check.events) == 1
    assert n1.parent is v1.scene
    assert n1.scene_node is v1.scene
    assert n1.document_node is c.scene

    n2 = Node(parent=n1)
    n2_parent_check = EventCheck(n2.events.parent_change)
    assert n2.parent is n1
    assert n2.scene_node is v1.scene
    assert n2.document_node is c.scene
    assert len(n1_child_check.events) == 1

    assert len(grid_check.events) == 2

    v2.add(n1)
    assert len(grid_check.events) == 2
    assert len(n1_parent_check.events) == 1
    assert len(n2_parent_check.events) == 1
    assert n1.parent is v2.scene
    assert n2.scene_node is v2.scene
    assert n2.document_node is c.scene


def test_transforms():
    # test transform mapping between nodes
    root = Node()
    n1 = Node(parent=root)
    n2 = Node(parent=n1)
    n3 = Node(parent=root)
    n4 = Node(parent=n3)

    n1.transform = STTransform(scale=(0.1, 0.1), translate=(7, 6))
    n2.transform = STTransform(scale=(0.2, 0.3), translate=(5, 4))
    n3.transform = STTransform(scale=(0.4, 0.5), translate=(3, 2))
    n4.transform = STTransform(scale=(0.6, 0.7), translate=(1, 0))

    assert np.allclose(n1.transform.map((0, 0))[:2], (7, 6))
    assert np.allclose(n1.node_transform(root).map((0, 0))[:2], (7, 6))
    assert np.allclose(n2.transform.map((0, 0))[:2], (5, 4))
    assert np.allclose(n2.node_transform(root).map((0, 0))[:2], 
                       (5*0.1+7, 4*0.1+6))
    assert np.allclose(root.node_transform(n1).map((0, 0))[:2],
                       (-7/0.1, -6/0.1))
    assert np.allclose(root.node_transform(n2).map((0, 0))[:2],
                       ((-7/0.1-5)/0.2, (-6/0.1-4)/0.3))

    # just check that we can assemble transforms correctly mapping across the
    # scenegraph
    assert n2.node_path(n4) == ([n2, n1, root], [n3, n4])
    assert n4.node_path(n2) == ([n4, n3, root], [n1, n2])
    assert n2.node_path(root) == ([n2, n1, root], [])
    assert root.node_path(n4) == ([root], [n3, n4])
    assert n2.node_path_transforms(n4) == [n4.transform.inverse, 
                                           n3.transform.inverse, 
                                           n1.transform, n2.transform]
    assert n4.node_path_transforms(n2) == [n2.transform.inverse,
                                           n1.transform.inverse,
                                           n3.transform, n4.transform]

    pts = np.array([[0, 0], [1, 1], [-56.3, 800.2]])
    assert np.all(n2.node_transform(n1).map(pts) == n2.transform.map(pts))
    assert np.all(n2.node_transform(root).map(pts) == 
                  n1.transform.map(n2.transform.map(pts)))
    assert np.all(n1.node_transform(n3).map(pts) == 
                  n3.transform.inverse.map(n1.transform.map(pts)))
    assert np.all(n2.node_transform(n3).map(pts) == 
                  n3.transform.inverse.map(
                      n1.transform.map(n2.transform.map(pts))))
    assert np.all(n2.node_transform(n4).map(pts) == 
                  n4.transform.inverse.map(n3.transform.inverse.map(
                      n1.transform.map(n2.transform.map(pts)))))

    # test transforms still work after reparenting
    n3.parent = n1
    assert np.all(n2.node_transform(n4).map(pts) == n4.transform.inverse.map(
        n3.transform.inverse.map(n2.transform.map(pts))))

    # test transform simplification
    assert np.all(n2.node_transform(n4).map(pts) == 
                  n2.node_transform(n4).simplified.map(pts))    


run_tests_if_main()
