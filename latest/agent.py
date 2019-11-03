# ============================================================
# Prediction Market Simulation - Agent
# ============================================================
#
# A number of agents participate concurrently in a market.
# They are able to buy and sell contracts whichpay off in 
# case of either a positive ('for') or a negative ('against') 
# outcome of a particular event.
# The behavior of an agent is determined on a set of rules 
# which model its belief (on the probability of the event), 
# its wealth and market price into the actions of buying and 
# selling the contracts.
#
# Agents concur in the market with the scope of profit.
#
# =============================================================

import heapq
from bid import Bid

TICK_SIZE = 0.01                 # Smallest discrete unit of price
TIME = 0                         # Allows the bids/asks to be ordered chronologically


class Agent:
    """ Class representing agents participating in the market.

    Attributes:
        ID: Numerical integer index for identification of an agent.
        starting_belief: Value in range [0.0, 1] representing the
            probability of the event to have a positive outcome 
            from the agent's point of view.
        risk_factor: Value determining the number of contracts the agent 
            will buy. [Contracts_Amount = (Belief - Price) * 100 * Risk]
        trust: Value determining how much the agents trust the market 
            price as an indicator of the probability of the outcome.
            Regularization factor for bayesian updating.
        wealth: Units of currency owned by a single agent. Every contract
            costs [0.0 < price < 1.0] and price_for = (1.0 - price_against).
        n_contracts_for: The number of contracts paying for the positive
            outcome possessed by the agent.
        n_contracts_against: The number of contracts paying for the negative
            outcome possessed by the agent.
    """
    
    def __init__(self, ID, starting_belief, risk_factor, trust, wealth):
        self.ID = ID
        self.belief = starting_belief
        self.risk_factor = risk_factor
        self.trust = trust
        self.wealth = wealth
        self.n_contracts_for = 0
        self.n_contracts_against = 0
        
    def update_belief_given_market(self, bayes_factor):
        """ Assuming the market has updated based on some evidence, 
            update your own belief based on that evidence.
            
            Args:
                bayes_factor: Factor for scaling probabilities 
                    with Bayesian Updating.
            """
        adjusted_bayes_factor = (self.trust*bayes_factor) + (1-self.trust)
        old_belief = self.belief
        new_belief = old_belief / (old_belief + adjusted_bayes_factor*(1-old_belief))
        self.belief = new_belief
    
    def for_main(self, bids_for, bids_against, market_price):
        """ Checks if the agents want to buy contracts for the
            positive outcome ('FOR') and stacks bids.
            FOR contracts cost (market_price).
                
            Args:
                bids_for: List of stacked Bids for contracts
                    for the positive outcome.
                bids_against: List of stacked Bids for contracts
                    for the negative outcome.
                market_price: The current price of the contracts.
                """
        max_for = heapq.nsmallest(1, bids_for)
        max_against = heapq.nsmallest(1, bids_against)
        buy_price = 1

        if max_for == []:                                                                       # No positive Bids have been placed yet.
            if max_against == []:                                                               # No negative Bids have been placed yet.
                buy_price = market_price + TICK_SIZE
            else:
                buy_price = 1 - max_against[0].price                                            # Offer to buy at the cheapest price.
        else:
            buy_price = max_for[0].price + TICK_SIZE                                            # Offer to buy at TICK_SIZE more than the next highest Bid.
            
        n_would_like_to_buy = int((self.belief-buy_price)*100*self.risk_factor)                 # Determine number of contract to buy with risk_factor
        n_can_buy = int(self.wealth/buy_price) + self.n_contracts_against
        n_will_buy = min(n_would_like_to_buy, n_can_buy)
        
        while n_will_buy > 0:                                                                   # Place Bids for contracts.
            self.place_bid_for(bids_for, buy_price)
            n_will_buy -= 1
    
    def against_main(self, bids_for, bids_against, market_price):
        """ Checks if the agents want to buy contracts for the
            negative outcome ('AGAINST') and stacks bids. 
            AGAINST contracts cost (1 - market_price).
                
            Args:
                bids_for: List of stacked Bids for contracts
                    for the positive outcome.
                bids_against: List of stacked Bids for contracts
                    for the negative outcome.
                market_price: The current price of the contracts.
                """
        max_for = heapq.nsmallest(1, bids_for)
        max_against = heapq.nsmallest(1, bids_against)
        buy_price = 1
        against_belief = 1-self.belief 
        
        if max_against == []:                                                                   # No positive Bids have been placed yet.
            if max_for == []:                                                                   # No negative Bids have been placed yet.
                buy_price = (1-market_price) + TICK_SIZE
            else:
                buy_price = 1 - max_for[0].price                                                # Offer to buy at cheapest price.
        else:
            buy_price = max_against[0].price
            buy_price += TICK_SIZE                                                              # Offer to buy at TICK_SIZE more than highest bid.
            
        n_would_like_to_buy = int((against_belief-buy_price)*100*self.risk_factor)              # Determine number of contract to buy with risk_factor
        n_can_buy = int(self.wealth/buy_price) + self.n_contracts_for
        n_will_buy = min(n_would_like_to_buy, n_can_buy)

        while n_will_buy > 0:                                                                   # Place Bids for contracts.
            self.place_bid_against(bids_against, buy_price)
            n_will_buy -= 1

    def place_bid_for(self, bids_for, bidding_price):
        global TIME
        new_bid = Bid("FOR", bidding_price, TIME, self.ID)
        heapq.heappush(bids_for, new_bid)
        TIME += 1                                                                               # Increment the time every time a bid/ask is placed
    
    def place_bid_against(self, bids_against, bidding_price):
        global TIME
        new_bid = Bid("AGAINST", bidding_price, TIME, self.ID)
        heapq.heappush(bids_against, new_bid)
        TIME += 1                                                                               # Increment the time every time a bid/ask is placed