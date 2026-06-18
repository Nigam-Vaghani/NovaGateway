import pytest
from app.load_balancer import RoundRobinBalancer, WeightedRoundRobinBalancer

class MockBackend:
    def __init__(self, id, url, weight=1):
        self.id = id
        self.url = url
        self.weight = weight

def test_round_robin_lb():
    lb = RoundRobinBalancer()
    backends = [MockBackend(1, "http://b1"), MockBackend(2, "http://b2")]
    
    selected_1 = lb.select_backend(backends)
    selected_2 = lb.select_backend(backends)
    selected_3 = lb.select_backend(backends)
    
    assert selected_1.id == 1
    assert selected_2.id == 2
    assert selected_3.id == 1

def test_weighted_lb():
    lb = WeightedRoundRobinBalancer()
    b1 = MockBackend(1, "http://b1", weight=2)
    b2 = MockBackend(2, "http://b2", weight=1)
    backends = [b1, b2]
    
    selected_1 = lb.select_backend(backends)
    selected_2 = lb.select_backend(backends)
    selected_3 = lb.select_backend(backends)
    
    assert selected_1.id in [1, 2]
    assert selected_2.id in [1, 2]
    assert selected_3.id in [1, 2]
