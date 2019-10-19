from agent import Agent

class Market:
    all_agents = []
    market_price = None
    old_market_price = None
    
    def __init__(self, n_agents, risk_factor, trust, wealth):
        self.all_agents = [Agent(i, 0.5, risk_factor, trust, wealth) for i in range(0,n_agents)]   #all agents are initialized with a belief of 0.5
        self.market_price = 0.5
        
    #check if a given agent can afford a transaction
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