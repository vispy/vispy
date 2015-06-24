# -*- coding: utf-8 -*-
from vispy.scene.node import Node
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)


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
    
    w = c.central_widget
    assert w.parent is c.scene
    assert w.scene_node is c.scene
    assert w.document_node is c.scene
    
    g = w.add_grid()
    
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
    
    
run_tests_if_main()
