import random
from typing import List
from app.models.routing import Backend

class LoadBalancer:
    def select_backend(self, backends: List[Backend]) -> Backend:
        raise NotImplementedError

class RoundRobinBalancer(LoadBalancer):
    def __init__(self):
        self.counter = 0

    def select_backend(self, backends: List[Backend]) -> Backend:
        if not backends:
            return None
        # Sort backends for consistent ordering
        sorted_backends = sorted(backends, key=lambda b: str(b.id))
        backend = sorted_backends[self.counter % len(sorted_backends)]
        self.counter += 1
        return backend

class WeightedRoundRobinBalancer(LoadBalancer):
    def select_backend(self, backends: List[Backend]) -> Backend:
        if not backends:
            return None
        total_weight = sum(b.weight for b in backends)
        if total_weight == 0:
            # Fallback to random if all weights are 0
            return random.choice(backends)
        
        pick = random.uniform(0, total_weight)
        current = 0
        
        sorted_backends = sorted(backends, key=lambda b: str(b.id))
        for backend in sorted_backends:
            current += backend.weight
            if current >= pick:
                return backend
        return sorted_backends[-1]

_round_robin = RoundRobinBalancer()
_weighted = WeightedRoundRobinBalancer()

def get_load_balancer(strategy: str) -> LoadBalancer:
    if strategy == "weighted":
        return _weighted
    return _round_robin
