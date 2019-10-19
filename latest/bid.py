
class Bid:
    type_bid = None #Is it an ask or a bid?
    price = None
    age = None
    agent_id = None
    priority = None #this is for heapq to properly sort the heap (you can ignore it)
    
    def __lt__(self, other):
        return self.priority < other.priority
    
    def __init__(self, type_bid, price, age, agent_id):
        self.type_bid = type_bid
        self.price = price
        self.age = age
        self.agent_id = agent_id
        self.priority = price * -1