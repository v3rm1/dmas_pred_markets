import random
import heapq

MAX_ITER = 50

TIME = 0 #This will be the time which will allow the bids/asks to be ordered based on how old they are

class Market:
    all_agents = []
    market_price = 0.5
    
    def __init__(self, n):
        low = random.uniform(0,0.4)
        high = random.uniform(0.6,1)
        self.all_agents = [Agent(i, low, high) for i in range(0,n)]
        
    def is_broke(self, agent_id, price):
        if self.all_agents[agent_id].wealth < price:
            return True
        return False
        
    def resolve_contracts(self, agent_id):      #if an agent holds a contract for and against, it can be exchanged for 1
        self.all_agents[agent_id].n_contracts_against -= 1
        self.all_agents[agent_id].n_contracts_for -= 1
        self.all_agents[agent_id].wealth += 1
        
    def buy_for(self, agent_id, price):
        self.all_agents[agent_id].wealth -= price
        self.all_agents[agent_id].n_contracts_for += 1        
        if self.all_agents[agent_id].n_contracts_against > 0:
            self.resolve_contracts(agent_id)
    
    def buy_against(self, agent_id, price):
        self.all_agents[agent_id].wealth -= (1-price)
        self.all_agents[agent_id].n_contracts_against += 1
        if self.all_agents[agent_id].n_contracts_for > 0:
            self.resolve_contracts(agent_id)

class Bid:
    type_bid = None #Is it an ask or a bid?
    price = None
    age = None
    agent_id = None
    priority = None
    
    def __lt__(self, other):
        return self.priority < other.priority
    
    def __init__(self, type_bid, price, age, agent_id):
        self.type_bid = type_bid
        self.price = price
        self.age = age
        self.agent_id = agent_id
        self.priority = price * -1

class Agent:
    belief = None
    wealth = None
    n_contracts_for = None
    n_contracts_against = None
    
    def __init__(self, i_d, low, high):
        self.i_d = i_d
        self.belief = random.uniform(low,high)
        self.wealth = 10
        self.n_contracts_for = 0
        self.n_contracts_against = 0
        
    def for_main(self, bids_for, bids_against):
        max_for = heapq.nsmallest(1, bids_for)
        max_against = heapq.nsmallest(1, bids_against)
        
        buy_price = 1
        
        if max_for == []:            #if no bids_for have been placed yet
            if max_against == []:       #if no bids_against have been placed yet
                buy_price = self.belief/2            #offer to buy at half the price you think it's worth
            else:
                buy_price = 1 - max_against[0].price             #offer to buy at the cheapest price
        else:
            buy_price = max_for[0].price 
            buy_price += 0.01               #offer to buy at 1 cent more than the next highest bid
        
        if buy_price < self.belief - 0.05:           #if the price is less than you think it's worth (0.05 represents risk aversion)
            if self.wealth >= buy_price:              #if you can afford the price
                #print("\tBelief: ", self.belief, "\tOffer for: ", buy_price)
                place_bid_for(self, bids_for, buy_price)
    
    def against_main(self, bids_for, bids_against):
        max_for = heapq.nsmallest(1, bids_for)
        max_against = heapq.nsmallest(1, bids_against)
        buy_price = 1
        against_belief = 1-self.belief
        
        if max_against == []:           #if no bids_against have been placed yet
            if max_for == []:           #if no bids_for have been placed yet
                buy_price = against_belief/2      #offer to buy for half what you think it's worth
            else:
                buy_price = 1 - max_for[0].price          #offer to buy at cheapest price
        else:
            sell_price = max_against[0].price
            sell_price += 0.01            #offer to buy at 1 cent more than highest bid
        
        if buy_price < against_belief - 0.05:         #if the price is less than you think it's worth (0.05 represents risk aversion)
            if self.wealth >= buy_price:              #if you can afford the price
                #print("\tBelief: ", self.belief, "\tOffer against: ", buy_price)
                place_bid_against(self, bids_against, buy_price)
        
def place_bid_for(a, bids_for, bidding_price):
    global TIME
    new_bid = Bid("for", bidding_price, TIME, a.i_d)
    heapq.heappush(bids_for, new_bid)
    TIME += 1 #increment the time every time a bid/ask is placed
    
def place_bid_against(a, bids_against, bidding_price):
    global TIME
    new_bid = Bid("against", bidding_price, TIME, a.i_d)
    heapq.heappush(bids_against, new_bid)
    TIME += 1 #increment the time every time a bid/ask is placed
    
def get_older_price(bid_for, bid_against):
    if bid_for.age < bid_for.age:
        return bid_for.price
    else:
        return 1 - bid_against.price
        
def collect_payment(agent_id, price, all_agents):
    all_agents[agent_id].wealth -= price
    all_agents[agent_id].n_contracts_for += 1
    
def pay_out_to(agent_id, price, all_agents):
    all_agents[agent_id].wealth += price
    all_agents[agent_id].n_contracts_for -= 1
    
def transact(bids_for, bids_against, market):
    if bids_for == [] or bids_against == []:
        return
    
    highest_bid_for = heapq.nsmallest(1, bids_for)[0]
    highest_bid_against = heapq.nsmallest(1, bids_against)[0]
    
    if market.is_broke(highest_bid_for.agent_id, highest_bid_for.price):    #if agent can't pay, delete bid
        heapq.heappop(bids_for)
        transact(bids_for, bids_against, market)
        return
        
    if market.is_broke(highest_bid_against.agent_id, highest_bid_against.price):    #if agent can't pay, delete bid
        heapq.heappop(bids_against)
        transact(bids_for, bids_against, market)
        return
    
    if(highest_bid_for.price + highest_bid_against.price >= 1):   #if 2 agents are offering enough to create a contract pair
        bid_for = heapq.heappop(bids_for)
        bid_against = heapq.heappop(bids_against)
        
        market_price = get_older_price(bid_for, bid_against)      #market price is the price of the most recent transaction
        market.buy_for(bid_for.agent_id, market_price)
        market.buy_against(bid_against.agent_id, market_price)
        
        #print("For: ", market.all_agents[bid_for.agent_id].belief, "\tAgainst: ", market.all_agents[bid_against.agent_id].belief)
        
        market.market_price = market_price                  #set the new market price after transaction
        
def main():
    print("Creating 100 agents...\n")
    market = Market(100)

    bids_against = []
    heapq.heapify(bids_against)
    bids_for = []
    heapq.heapify(bids_against)
    for i in range(0, MAX_ITER):
        all_agents = market.all_agents.copy()
        random.shuffle(all_agents)
        for a in all_agents:
            #print(a.i_d)
            
            a.for_main(bids_for, bids_against)                 
            a.against_main(bids_for, bids_against)              
            
            transact(bids_for, bids_against, market)
        
        print("Iter: ", i, "\tMarket Price: ", market.market_price)
        
    all_beliefs = [market.all_agents[i].belief for i in range(0,100)]
    average = sum(all_beliefs) / len(all_beliefs)
    print("Average Belief: ", average)
    
    for a in market.all_agents:
        print("Belief: ", a.belief, "\tFor: ", a.n_contracts_for, "\tAgainst: ", a.n_contracts_against, "\tWealth: ", a.wealth)

    
    #import pdb; pdb.set_trace()
    

if __name__ == "__main__":
    main()
