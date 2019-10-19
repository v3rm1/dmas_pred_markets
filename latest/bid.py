# ============================================================
# Prediction Market Simulation - Bid
# ============================================================
#
# A number of agents participate concurrently in a market.
# They are able to buy and sell contracts whichpay off in 
# case of either a positive ('for') or a negative ('against') 
# outcome of a particular event.
#
# Agents place bids to exchange contracts.
#
# =============================================================
class Bid:
    """ Class representing a bid for a contract.
    
    Attributes:
        type_bid: String in {'FOR', 'AGAINST'}, sets the 
            type of contract to bid for.
        price: The cost of the contract at the moment of 
            the transaction.
        age: The TIME value to sort the Bids chronologically.
        agent_id: Agent.ID value for the bidding agent.
        priority: Value needed for heapq to sort the heap by 
            price.
    """
    def __lt__(self, other):
        return self.priority < other.priority
    
    def __init__(self, type_bid, price, age, agent_id):
        self.type_bid = type_bid
        self.price = price
        self.age = age
        self.agent_id = agent_id
        self.priority = price * -1