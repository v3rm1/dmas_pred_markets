# ============================================================
# Prediction Market Simulation - Market
# ============================================================
#
# A number of agents participate concurrently in a market.
# They are able to buy and sell contracts whichpay off in 
# case of either a positive ('for') or a negative ('against') 
# outcome of a particular event.
#
# Agents concur in the market with the scope of profit.
#
# The market price of the contracts should approximate the
# true probability of the interested event, assuming a role
# of agglomerate of information of the agents.
#
# =============================================================

from agent import Agent
from numpy import random

class Market:
    """ Class representing the prediction market.
    Initialize the agents and manages the transactions
    for the contracts.

    Attributes:
        all_agents: List of all the agents in the market.
        market_price: The determined value of the contracts.
        old_market_price: The value of the contracts for the 
            previous cycle.
    """
    all_agents = []
    market_price = None
    old_market_price = None
    
    def __init__(self, n_agents, risk_factor, trust, wealth, belief_random=False):
        """ Initialize market.
        
        Args:
            n_agents: Number of agents concurring in the market.
            risk_factor: Value determining the number of contracts the agent 
                will buy. [Contracts_Amount = (Belief - Price) * 100 * Risk]
            trust: Value determining how much the agents trust the market 
                price as an indicator of the probability of the outcome.
                Regularization factor for bayesian updating.
            wealth: Units of currency owned by a single agent. Every contract
                costs [0.0 < price < 1.0] and price_for = (1.0 - price_against).
        """
        if (belief_random):
            believes = random.uniform(low=0.05, high=0.95, size=n_agents)
            self.all_agents = [Agent(i, believes[i], risk_factor, trust, wealth) for i in range(0,n_agents)]
        else:
            self.all_agents = [Agent(i, 0.5, risk_factor, trust, wealth) for i in range(0,n_agents)]
        self.market_price = 0.5
        
    def is_broke(self, agent_id, price, type_purchase):
        """ Checks if an agent can afford to pay for a contract.
        
        Args:
            agent_id: Agent.ID value for the agent to check.
            price: The market price at the moment of the transaction.
            type_purchase: String in {'FOR', 'AGAINST'} to indicate the
                type of contract to be bought.

        Returns
            A boolean value, True if the agant can afford the contract,
                False otherwise.
            """
        if self.all_agents[agent_id].wealth < price:
            if type_purchase == "FOR" and self.all_agents[agent_id].n_contracts_against >= 1:               # If they have a contract against to sell, they aren't broke.
                return False
            if type_purchase == "AGAINST" and self.all_agents[agent_id].n_contracts_for >= 1:               # If they have a contract against to sell, they aren't broke.
                return False
            return True
        return False
        
    def resolve_contracts(self, agent_id):
        """ Check if an agent holds a contract FOR and AGAINST, 
            it is exchanged for 1 unit of currency."""
        self.all_agents[agent_id].n_contracts_against -= 1
        self.all_agents[agent_id].n_contracts_for -= 1
        self.all_agents[agent_id].wealth += 1
        
    def buy_for(self, agent_id, price):
        """ Resolve the transaction for a FOR contract."""
        self.all_agents[agent_id].wealth -= price
        self.all_agents[agent_id].n_contracts_for += 1
        if self.all_agents[agent_id].n_contracts_against > 0:
            self.resolve_contracts(agent_id)
    
    def buy_against(self, agent_id, price):
        """ Resolve the transaction for an AGAINST contract."""
        self.all_agents[agent_id].wealth -= (1-price)
        self.all_agents[agent_id].n_contracts_against += 1
        if self.all_agents[agent_id].n_contracts_for > 0:
            self.resolve_contracts(agent_id)    