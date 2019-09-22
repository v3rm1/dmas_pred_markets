import random
import heapq

MAX_ITER = 100

TIME = 0 #This will be the time which will allow the bids/asks to be ordered based on how old they are

class Market:
    all_agents = []
    market_price = 0.5
    
    def __init__(self, n):
        low = random.uniform(0,0.4)
        high = random.uniform(0.6,1)
        self.all_agents = [Agent(i, low, high) for i in range(0,n)]
        
    def buy(self, agent_id, price):
        self.all_agents[agent_id].wealth -= price
        self.all_agents[agent_id].n_contracts_for += 1
    
    def sell(self, agent_id, price):
        self.all_agents[agent_id].wealth += price
        self.all_agents[agent_id].n_contracts_for -= 1

class Bid:
    type_bid = None #Is it an ask or a bid?
    price = None
    age = None
    agent_id = None
    
    def __init__(self, type_bid, price, age, agent_id):
        self.type_bid = type_bid
        self.price = price
        self.age = age
        self.agent_id = agent_id

class Agent:
    belief = None
    wealth = None
    n_contracts_for = None
    n_contracts_against = None
    
    def __init__(self, i_d, low, high):
        self.i_d = i_d
        self.belief = random.uniform(low,high)
        self.wealth = 10
        self.n_contracts_for = 10
        
    def buy_main(self, bids, asks):
        largest = heapq.nlargest(1, bids)
        smallest = heapq.nsmallest(1, asks)
        buy_price = 1
        
        if largest == []:            #if no bids have been placed yet
            if smallest == []:       #if no asks have been placed yet
                buy_price = self.belief/2            #offer to buy at half the price you think it's worth
            else:
                (buy_price, _) = smallest[0]              #offer to buy at the cheapest ask price
        else:
            (buy_price, _) = largest[0] 
            buy_price += 0.01               #offer to buy at 1 cent more than the next highest bid
        
        if buy_price < self.belief - 0.05:           #if the price is less than you think it's worth (0.05 represents risk aversion)
            if self.wealth >= buy_price:              #if you can afford the price
                place_bid(self, bids, buy_price)
    
    def sell_main(self, bids, asks):
        largest = heapq.nlargest(1, bids)
        smallest = heapq.nsmallest(1, asks)
        sell_price = 0
        
        if smallest == []:           #if no asks have been placed yet
            if largest == []:        #if no bids have been placed yet
                sell_price = 1-(1-self.belief)/2      #offer to sell for more than you think it's worth (0.6-->0.8), (0.9-->0.95)
            else:
                (sell_price, _) = largest[0]              #offer to sell at the highest bid price
        else:
            (sell_price, _) = smallest[0]
            sell_price -= 0.01            #offer to sell at 1 cent less than the next lowest ask
        
        if sell_price > self.belief + 0.05:           #if the price is more than you think it's worth (0.05 represents risk aversion)
            if self.n_contracts_for > 0:                #if you actually have a contract to sell
                place_bid(self, asks, sell_price)
        
def place_bid(a, bids, bidding_price):
    global TIME
    new_bid = Bid("bid", bidding_price, TIME, a.i_d)
    heapq.heappush(bids, (bidding_price, new_bid))
    TIME += 1 #increment the time every time a bid/ask is placed
    
def place_ask(a, asks, asking_price):
    global TIME
    new_ask = Bid("ask", asking_price, TIME, a.i_d)
    heapq.heappush(asks, (asking_price, new_ask))
    TIME += 1 #increment the time every time a bid/ask is placed
    
def get_older_price(bid, ask):
    if bid.age < ask.age:
        return bid.price
    else:
        return ask.price
        
def collect_payment(agent_id, price, all_agents):
    all_agents[agent_id].wealth -= price
    all_agents[agent_id].n_contracts_for += 1
    
def pay_out_to(agent_id, price, all_agents):
    all_agents[agent_id].wealth += price
    all_agents[agent_id].n_contracts_for -= 1
    
def transact(asks, bids, market):
    if bids == [] or asks == []:
        return
    
    (highest_bid, _) = heapq.nlargest(1, bids)[0]
    (lowest_ask, _) = heapq.nsmallest(1, asks)[0]
    
    if(highest_bid >= lowest_ask):
        (_, bid) = heapq._heappop_max(bids)
        (_, ask) = heapq.heappop(asks)
        market_price = get_older_price(bid, ask)      #market price is the price of the oldest bid/ask in the most recent transaction
        market.buy(bid.agent_id, market_price)
        market.sell(ask.agent_id, market_price)
        
    market.market_price = market_price                  #set the new market price after transaction
        
def main():
    print("Creating 100 agents...\n")
    market = Market(100)

    asks = []
    heapq.heapify(asks)
    bids = []
    heapq._heapify_max(bids)
    for i in range(0, MAX_ITER):
        all_agents = market.all_agents
        random.shuffle(all_agents)
        for a in all_agents:
            
            a.sell_main(bids, asks)             #the main sell script for the agent
            a.buy_main(bids, asks)              #the main buy script for the agent
            
            transact(asks, bids, market)
        
        print("Iter: ", i, "\tMarket Price: ", market.market_price)
        
    all_beliefs = [market.all_agents[i].belief for i in range(0,100)]
    average = sum(all_beliefs) / len(all_beliefs)
    print("Average Belief: ", average)
    
    
    #import pdb; pdb.set_trace()
    

if __name__ == "__main__":
    main()
