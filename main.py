import random
import heapq
import argparse
#import pandas as pd                I do all my programming on Peregrine, and I don't know how to get pandas....
#import matplotlib.pyplot as plt                        ^^^ see above. If anyone knows, please let me know :)

# Tommy: There's a page on the wiki about installing packages: 
# https://redmine.hpc.rug.nl/redmine/projects/peregrine/wiki/Installation_of_extra_applications_or_libraries_(make_pip_or_R)
# Should be just a couple lines in the script

parser = argparse.ArgumentParser(description='Parameters of the Prediction Market simulation.')
parser.add_argument('-n', metavar="NUM_AGENTS", default=100, type=int, help='Provide the number of agents in the market (default: 100)')
parser.add_argument('-i', metavar="NUM_ITERATIONS", default=100, type=int, help='Provide the number of iterations of the market (default: 50)')

args = parser.parse_args()

N_AGENTS = args.n
MAX_ITER = args.i

N_EVIDENCE = 20
FRACTION_RECEIVING_EVIDENCE = 0.1
FRACTION_EXTRA_TIME = 0.5
EVIDENCE_TIME = int((1-FRACTION_EXTRA_TIME)*MAX_ITER)

RISK = 0.05

TIME = 0 #This will be the time which will allow the bids/asks to be ordered based on how old they are

class Market:
    all_agents = []
    market_price = None
    
    def __init__(self, n):
        self.all_agents = [Agent(i, 0.5) for i in range(0,n)]
        
    def is_broke(self, agent_id, price, type_purchase):
        if self.all_agents[agent_id].wealth < price:
            if type_purchase == "FOR" and self.all_agents[agent_id].n_contracts_against >= 1: #if they have a contract against to sell, they aren't really broke!
                return False
            if type_purchase == "AGAINST" and self.all_agents[agent_id].n_contracts_for >= 1: 
                return False
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
    
    def __init__(self, i_d, starting_belief):
        self.i_d = i_d
        self.belief = starting_belief
        self.wealth = 100
        self.n_contracts_for = 0
        self.n_contracts_against = 0
        
    def for_main(self, bids_for, bids_against, market_price):
        max_for = heapq.nsmallest(1, bids_for)
        max_against = heapq.nsmallest(1, bids_against)
        
        buy_price = 1
        
        if max_for == []:            #if no bids_for have been placed yet
            if max_against == []:       #if no bids_against have been placed yet
                if market_price == None:
                    buy_price = self.belief/2          #offer to buy at half the price you think it's worth (this choice is arbitrary, there is no market information yet about the actual value)
                else:
                    buy_price = market_price + 0.001
            else:
                buy_price = 1 - max_against[0].price             #offer to buy at the cheapest price
        else:
            buy_price = max_for[0].price 
            buy_price += 0.001               #offer to buy at 1 cent more than the next highest bid
        
        if buy_price < self.belief - RISK:           #if the price is less than you think it's worth (0.05 represents risk aversion)
            if self.wealth >= buy_price or self.n_contracts_against >= 1:              #if you can afford the price, or you have a contract against to sell
                #print("\tBelief: ", self.belief, "\tOffer for: ", buy_price)
                place_bid_for(self, bids_for, buy_price)
    
    def against_main(self, bids_for, bids_against, market_price):
        max_for = heapq.nsmallest(1, bids_for)
        max_against = heapq.nsmallest(1, bids_against)
        buy_price = 1
        against_belief = 1-self.belief
        
        if max_against == []:           #if no bids_against have been placed yet
            if max_for == []:           #if no bids_for have been placed yet
                if market_price == None:
                    buy_price = against_belief/2      #offer to buy for half what you think it's worth (this choice is arbitrary, there is no market information yet about the actual value)
                else:
                    buy_price = (1-market_price) + 0.001
            else:
                buy_price = 1 - max_for[0].price          #offer to buy at cheapest price
        else:
            buy_price = max_against[0].price
            buy_price += 0.001            #offer to buy at 1 cent more than highest bid

        if buy_price < against_belief - RISK:         #if the price is less than you think it's worth (0.05 represents risk aversion)
            if self.wealth >= buy_price or self.n_contracts_for >= 1:              #if you can afford the price, or you have a contract for to sell
                #print("\tBelief: ", self.belief, "\tOffer against: ", buy_price)
                place_bid_against(self, bids_against, buy_price)
                
class God:
    def __init__(self, p_AgivenE, p_BgivenE):
        self.belief = 0.5
        self.p_AgivenE = p_AgivenE
        self.p_BgivenE = p_BgivenE
        self.p_A = 0.5
        self.p_B = 0.5
        self.p_Agiven_notE = 2*self.p_A - self.p_AgivenE        
        self.p_Bgiven_notE = 2*self.p_B - self.p_BgivenE      
    
    def get_answer_to_life_the_universe_and_everything():
        return 42
        
    def update_belief(self, old_belief, evidence):  #this updates a belief using bayes rule, given a new piece of evidence
        if evidence == "A":
            new_belief = (old_belief * self.p_AgivenE) / ((old_belief * self.p_AgivenE) + ((1-old_belief) * self.p_Agiven_notE))
        else:
            new_belief = (old_belief * self.p_BgivenE) / ((old_belief * self.p_BgivenE) + ((1-old_belief) * self.p_Bgiven_notE))
        return new_belief
        
    def update_universe(self, market, n_receiving_evidence):
        x = random.uniform(0,1)
        if x < self.p_A:
            evidence = "A"
        else:
            evidence = "B"
        self.belief = self.update_belief(self.belief, evidence)         #God updates their own belief
        
        #select a random set of agents to receive evidence
        all_agent_indices = [i for i in range(0, N_AGENTS)]
        random.shuffle(all_agent_indices)
        chosen_ones = all_agent_indices[:n_receiving_evidence]
        
        for i in range(0, len(chosen_ones)):
            agent_id = chosen_ones[i]
            old_belief = market.all_agents[agent_id].belief
            new_belief = self.update_belief(old_belief, evidence)
            market.all_agents[agent_id].belief = new_belief
        
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
    
def transact(bids_for, bids_against, market):
    if bids_for == [] or bids_against == []:
        return
    
    highest_bid_for = heapq.nsmallest(1, bids_for)[0]
    highest_bid_against = heapq.nsmallest(1, bids_against)[0]
    
    if market.is_broke(highest_bid_for.agent_id, highest_bid_for.price, "FOR"):    #if agent can't pay, delete bid
        heapq.heappop(bids_for)
        transact(bids_for, bids_against, market)
        return
        
    if market.is_broke(highest_bid_against.agent_id, highest_bid_against.price, "AGAINST"):    #if agent can't pay, delete bid
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
    the_almighty = God(0.6, 1-0.6)
    
    iters_per_evidence = int(EVIDENCE_TIME/N_EVIDENCE)
    
    print("Creating {} agents...\n".format(N_AGENTS))
    market = Market(N_AGENTS)
    # data = pd.DataFrame(columns=['iter', 'agent_id', 'belief', 'wealth', 'n_for', 'n_against', 'market_price'])
    price_history = []

    bids_against = []
    heapq.heapify(bids_against)
    bids_for = []
    heapq.heapify(bids_against)
    for i in range(0, MAX_ITER):
        if i < EVIDENCE_TIME:    #allow for extra time after evidence to just trade
            if i%iters_per_evidence == 0:
                the_almighty.update_universe(market, int(N_AGENTS * FRACTION_RECEIVING_EVIDENCE))     
                #print("God has spoken!")       
        
        all_agents = market.all_agents.copy()
        random.shuffle(all_agents)
        for a in all_agents:
            
            a.for_main(bids_for, bids_against, market.market_price) 
            a.against_main(bids_for, bids_against, market.market_price)  
                            
            
            transact(bids_for, bids_against, market)
            # data.loc[(i*N_AGENTS)+a.i_d] = [i, a.i_d, a.belief, a.wealth, a.n_contracts_for, a.n_contracts_against, market.market_price]
        
        print("Iter: ", i, "\tMarket Price: ", market.market_price)
        price_history.append(market.market_price)
    
    print("God's Belief: ", the_almighty.belief)
        
    all_beliefs = [market.all_agents[i].belief for i in range(0,N_AGENTS)]
    average = sum(all_beliefs) / len(all_beliefs)
    print("Average Belief: ", average)
    
    print("Final Market Price: ", market.market_price)
    
    print("\nAgent Summary:")
    
    for a in market.all_agents:
        print("Agent ID: ", a.i_d, "\tBelief: ", "{0:.2f}".format(a.belief), "\tFor: ", a.n_contracts_for, "\tAgainst: ", a.n_contracts_against, "\tWealth: ", "{0:.2f}".format(a.wealth))


    #import pdb; pdb.set_trace()
    
    #Yeah, sorry, until Peregrine and I sort out our differences, I can't use these. I love the graph though, really nice addition!

    #plt.figure(figsize=(12,4))
    #plt.plot(range(MAX_ITER), price_history)
    #plt.xlabel("Iterations (Market Cycles)")
    #plt.ylabel("Price")
    #plt.grid()
    #plt.show()


if __name__ == "__main__":
    main()
    
    
