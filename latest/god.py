""" Manages the probabilities of the system.

Evidence is either of type A or type B. 
Type A evidence indicates a higher probability of an event E 
occurring, while Type B evidence indicates a lower probability 
of E occurring. An agent receiving a unit of evidence updates 
its belief using Bayesian induction.

Attributes:
    belief: The initial probability of the event E, fixed at 0.5.
    n_agents: The number of agents in the system.
    p_AgivenE: Probability of the event A to happen given the event E.
    p_BgivenE: Probability of the event B to happen given the event E.
    p_A: Probability of event A, fixed = 0.5
    p_B: Probability of event B, fixed = 0.5
    p_Agiven_notE: Probability of the event A to happen given the event (not E) = 2*self.p_A - self.p_AgivenE
    p_Bgiven_notE: Probability of the event B to happen given the event (not E) = 2*self.p_B - self.p_BgivenE  
"""

import random

class God:
    def __init__(self, p_AgivenE, p_BgivenE, n_agents):
        """Initialize 'True Probability' and all probabilities
        required to Bayes update."""
        self.belief = 0.5
        self.n_agents = n_agents
        self.p_AgivenE = p_AgivenE
        self.p_BgivenE = p_BgivenE
        self.p_A = 0.5
        self.p_B = 0.5
        self.p_Agiven_notE = 2*self.p_A - self.p_AgivenE        
        self.p_Bgiven_notE = 2*self.p_B - self.p_BgivenE      
    
    def get_answer_to_life_the_universe_and_everything(self):
        """Easter Egg."""
        return 42
        
    def update_belief(self, old_belief, evidence):
        """Updates a belief using bayes rule, given a new piece of evidence."""
        if evidence == "A":
            new_belief = (old_belief * self.p_AgivenE) / ((old_belief * self.p_AgivenE) + ((1-old_belief) * self.p_Agiven_notE))
        else:
            new_belief = (old_belief * self.p_BgivenE) / ((old_belief * self.p_BgivenE) + ((1-old_belief) * self.p_Bgiven_notE))
        return new_belief
        
    def update_universe(self, market, n_receiving_evidence):
        """Update the 'True Probability' and update a selected number of agents' beliefs"""
        x = random.uniform(0,1)
        if x < self.p_A:
            evidence = "A"
        else:
            evidence = "B"
        self.belief = self.update_belief(self.belief, evidence)
        
        #select a random set of agents to receive evidence
        all_agent_indices = [i for i in range(0, self.n_agents)]
        random.shuffle(all_agent_indices)
        chosen_ones = all_agent_indices[:n_receiving_evidence]
        
        for i in range(0, len(chosen_ones)):
            agent_id = chosen_ones[i]
            old_belief = market.all_agents[agent_id].belief
            new_belief = self.update_belief(old_belief, evidence)
            market.all_agents[agent_id].belief = new_belief
        
