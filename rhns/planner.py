import heapq, itertools
class Planner:
    def __init__(self, proposer, complete, max_nodes=50, max_cost=1.0, w=(1.0, 0.5, 1.0, 1.0)):
        self.proposer, self.complete, self.max_nodes, self.max_cost, self.w = proposer, complete, max_nodes, max_cost, w
    def plan(self):
        wu, we, wr, wc = self.w
        n, tie = 0, itertools.count()
        heap = [(0.0, next(tie), [], 0.0)]
        while heap and n < self.max_nodes:
            negs, _, steps, cost = heapq.heappop(heap); n += 1
            if self.complete(steps):
                return steps
            for c in self.proposer(steps):
                nc = cost + c.get("cost", 0)
                if nc > self.max_cost: continue
                s = wu*c.get("utility", 0) + we*c.get("evidence", 0) - wr*c.get("risk", 0) - wc*c.get("cost", 0)
                heapq.heappush(heap, (negs - s, next(tie), steps + [c], nc))
        return None
