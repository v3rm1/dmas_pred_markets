""" 
Test script to determine relationship 
between parameters and correlation of market 
price and 'True Probability'.

Usage: python3 test.py

Output: ./results.csv
"""

import numpy as np
import random
import heapq
import argparse
import pandas as pd      
import matplotlib.pyplot as plt
import time
from god import God
from market import Market

    
def get_older_price(bid_for, bid_against):
    """Returns the price of the most recent transaction."""
    if bid_for.age < bid_for.age:
        return bid_for.price
    else:
        return 1 - bid_against.price
    
def transact(bids_for, bids_against, market):
    """Performs transactions.

    Recursevly resolves all the bids for contracts stacked by the agents.

    Args:
        bids_for: List of bids for contracts paying for positive outcome.
        bids_against: List of bids for contracts paying for negative outcome.
        market: The Market object to perform the transactions in.
    """
    if bids_for == [] or bids_against == []:
        return
    
    highest_bid_for = heapq.nsmallest(1, bids_for)[0]
    highest_bid_against = heapq.nsmallest(1, bids_against)[0]
    
    # Removes the bid if the agent can't pay.
    if market.is_broke(highest_bid_for.agent_id, highest_bid_for.price, "FOR"):
        heapq.heappop(bids_for)
        transact(bids_for, bids_against, market)
        return

    # Removes the bid if the agent can't pay.
    if market.is_broke(highest_bid_against.agent_id, highest_bid_against.price, "AGAINST"):
        heapq.heappop(bids_against)
        transact(bids_for, bids_against, market)
        return
    
    if(highest_bid_for.price + highest_bid_against.price >= 1):
        bid_for = heapq.heappop(bids_for)
        bid_against = heapq.heappop(bids_against)
        
        # Market price becomes the price of the most recent transaction.
        market_price = get_older_price(bid_for, bid_against)

        # Resolve transactions.
        market.buy_for(bid_for.agent_id, market_price)
        market.buy_against(bid_against.agent_id, market_price)
        
        # Sets the new market price
        market.market_price = market_price
        transact(bids_for, bids_against, market)
    else:
        return
        
def get_bayesian_update_factor(old_price, new_price, N_AGENTS):
    """TODO: discuss math behind this."""
    return (old_price*(1-new_price))/(new_price*(1-old_price))
    
def learn_from_market(market):
    """Updates the beliefs of the agents."""
    if market.market_price == None or market.old_market_price == None:
        return
    bayes_factor = get_bayesian_update_factor(market.old_market_price, market.market_price, len(market.all_agents))
    for i in range(0, len(market.all_agents)):
        market.all_agents[i].update_belief_given_market(bayes_factor)

def plot_dynamic(x, y, fig, ax, color):
    """Visualize results updating in real-time.
    
    Args:
        x: List of index of the N completed market cycles [0, 1, ..., N-1].
        y: List of market prices at the end each cycle.
        fig: Reference to a matplotlib.figure.Figure object, 
            e.g. fig = matplotlib.pyplot.figure().
        ax: Reference to the axes of the plot, 
            e.g. ax = matplotlib.pyplot.gca()
            or
            fig, ax = matplotlib.pyplot.subplots()
        color: str color for the plot.
    """
    ax.plot(x, y, color)
    plt.legend(['Market Price', 'True Bayesian Probability', 'Agent 0 Belief'])
    plt.xlabel("Iterations (Market Cycles)")
    plt.ylabel("Price")
    fig.canvas.draw()
    plt.pause(1e-17)
    time.sleep(0.00001)



def test(N_AGENTS, MAX_ITER, N_EVIDENCE, FRACTION_RECEIVING_EVIDENCE, FRACTION_EXTRA_TIME, RISK_FACTOR, TRUST, WEALTH):
    """Main cycle from 'run.py'."""

    EVIDENCE_TIME = int((1-FRACTION_EXTRA_TIME)*MAX_ITER)   # Number of cycles the agents keep on trading after all the evidence has been provided.

    # Exit the program if user inputs invalid arguments.
    if (RISK_FACTOR <= 0.0):
        print("Error: Invalid Argument for RISK_FACTOR: must be more than 0.0.")
        exit()
    if (TRUST > 1.0 or TRUST < 0.0):
        print("Error: Invalid Argument for TRUST: must be in range [0.0, 1.0].")
        exit()

    # We use this object to distribute evidence, 
    # and maintain the complete bayesian probability.
    the_almighty = God(0.6, 1-0.6, N_AGENTS) # TODO explain why 0.6 or put in an argument
    
    iters_per_evidence = np.round(EVIDENCE_TIME/N_EVIDENCE)
    
    market = Market(N_AGENTS, RISK_FACTOR, TRUST, WEALTH, belief_random=True)

    bids_against = []
    heapq.heapify(bids_against)
    bids_for = []
    heapq.heapify(bids_against)

    price_history = []
    god_history = []
    agent_0_history = []

    

    for i in range(0, MAX_ITER):
        # Allow for extra time after evidence to just trade.
        if i < EVIDENCE_TIME:
            if i%iters_per_evidence == 0:
                # All agents learn from recent changes in market price.
                learn_from_market(market)
                market.old_market_price = market.market_price
                
                the_almighty.update_universe(market, int(N_AGENTS * FRACTION_RECEIVING_EVIDENCE))     
                #print("God has spoken!")
        
        all_agents = market.all_agents.copy()
        random.shuffle(all_agents)
        for a in all_agents:
            
            # Place bids for or against the event outcome.
            a.for_main(bids_for, bids_against, market.market_price) 
            a.against_main(bids_for, bids_against, market.market_price)  
            
            # Trade contracts if possible.
            transact(bids_for, bids_against, market)
        
        price_history.append(market.market_price)
        god_history.append(the_almighty.belief)

        agent_0_history.append(all_agents[0].belief)


    return np.corrcoef(price_history, god_history) , (the_almighty.belief - market.market_price)

def main():
    """Cycles through every combination of the specified parameters parameters"""

    ## Full Version
    # test_agents = [50, 100]
    # test_iters = [50, 100, 200, 300]
    # test_evidence = [5, 10, 20]
    # test_fraction = [0.1, 0.25, 0.33, 0.50, 0.75]
    # test_trust = [0, 0.3, 0.5, 0.7, 1]
    # test_risk = [0.1, 0.5, 1.0, 1.5]

    # Reduced Version
    test_agents = [50, 100]
    test_iters = [100, 200]
    test_evidence = [20]
    test_fraction = [0.25, 0.50, 0.75]
    test_trust = [0, 0.5, 1]
    test_risk = [1]

    history_agents = []
    history_iters = []
    history_evidence = []
    history_fraction = []
    history_trust = []
    history_risk = []
    history_diff = []
    history_corr = []
    for n_agents in test_agents:
        for n_iters in test_iters:
            for n_evidence in test_evidence:
                for fraction in test_fraction:
                    for trust in test_trust:
                        for risk in test_risk:
                            correlation = []
                            difference = []
                            for i in range(25):
                                corr, diff = test(n_agents, n_iters, n_evidence, fraction, 0.1, risk, trust, 100)
                                correlation.append(np.min(corr))
                                difference.append(np.abs(diff))
                            history_agents.append(n_agents)
                            history_iters.append(n_iters)
                            history_evidence.append(n_evidence)
                            history_fraction.append(fraction)
                            history_trust.append(trust)
                            history_risk.append(risk)
                            history_diff.append(np.average(difference))
                            history_corr.append(np.average(correlation))
                            
    results = pd.DataFrame({"n_agents"                        : history_agents,
                  "n_iterations"                    : history_iters,
                  "n_evidence"                      : history_evidence,
                  "fraction receiving evidence"     : history_fraction,
                  "trust"                           : history_trust,
                  "risk"                            : history_risk,
                  "difference"                      : history_diff,
                  "correlation"                     : history_corr
                  })

    results.to_csv("./results.csv")


if __name__ == "__main__":
    main()
    
    
