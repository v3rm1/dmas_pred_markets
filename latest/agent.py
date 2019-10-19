import heapq
from bid import Bid

TICK_SIZE = 0.01  #This is the smallest discrete unit of price
TIME = 0 #This will be the time which will allow the bids/asks to be ordered based on how old they are


class Agent:
    belief = None
    wealth = None
    n_contracts_for = None
    n_contracts_against = None
    
    def __init__(self, i_d, starting_belief, risk_factor, trust, wealth):
        self.i_d = i_d
        self.belief = starting_belief
        self.risk_factor = risk_factor
        self.trust = trust
        self.wealth = wealth
        self.n_contracts_for = 0
        self.n_contracts_against = 0
        
    #Here, assuming the market has updated based on some invisible evidence, update your own belief based on that evidence
    def update_belief_given_market(self, bayes_factor):
        adjusted_bayes_factor = (1-self.trust) + (self.trust*bayes_factor)
        old_belief = self.belief
        new_belief = old_belief / (old_belief + adjusted_bayes_factor*(1-old_belief))
        self.belief = new_belief
        
    #Place bids "for" the proposition
    def for_main(self, bids_for, bids_against, market_price):
        max_for = heapq.nsmallest(1, bids_for)
        max_against = heapq.nsmallest(1, bids_against)
        
        buy_price = 1
        
        if max_for == []:            #if no bids_for have been placed yet
            if max_against == []:       #if no bids_against have been placed yet
                buy_price = market_price + TICK_SIZE
            else:
                buy_price = 1 - max_against[0].price             #offer to buy at the cheapest price
        else:
            buy_price = max_for[0].price + TICK_SIZE #offer to buy at 1 cent more than the next highest bid             
            
        n_would_like_to_buy = int((self.belief-buy_price)*100*self.risk_factor)
        n_can_buy = int(self.wealth/buy_price) + self.n_contracts_against
        n_will_buy = min(n_would_like_to_buy, n_can_buy)
        while n_will_buy > 0:
            self.place_bid_for(bids_for, buy_price)
            n_will_buy -= 1
    
    #Place bids "against" the proposition
    #Here, the price is market price is flipped: (1-market_price) If "for" contracts are trading for 90 cents, then "against" contracts are trading for 10 cents.
    def against_main(self, bids_for, bids_against, market_price):
        max_for = heapq.nsmallest(1, bids_for)
        max_against = heapq.nsmallest(1, bids_against)
        buy_price = 1
        against_belief = 1-self.belief 
        
        if max_against == []:           #if no bids_against have been placed yet
            if max_for == []:           #if no bids_for have been placed yet
                buy_price = (1-market_price) + TICK_SIZE
            else:
                buy_price = 1 - max_for[0].price          #offer to buy at cheapest price
        else:
            buy_price = max_against[0].price
            buy_price += TICK_SIZE            #offer to buy at 1 cent more than highest bid
            
        n_would_like_to_buy = int((against_belief-buy_price)*100*self.risk_factor)
        n_can_buy = int(self.wealth/buy_price) + self.n_contracts_for
        n_will_buy = min(n_would_like_to_buy, n_can_buy)
        while n_will_buy > 0:
            self.place_bid_against(bids_against, buy_price)
            n_will_buy -= 1

    def place_bid_for(self, bids_for, bidding_price):
        global TIME
        new_bid = Bid("for", bidding_price, TIME, self.i_d)
        heapq.heappush(bids_for, new_bid)
        TIME += 1 #increment the time every time a bid/ask is placed
    
    def place_bid_against(self, bids_against, bidding_price):
        global TIME
        new_bid = Bid("against", bidding_price, TIME, self.i_d)
        heapq.heappush(bids_against, new_bid)
        TIME += 1 #increment the time every time a bid/ask is placed