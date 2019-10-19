""" Prediction Market Simulation.

In prediction (or Information) markets participants trade in contracts whose 
payoff depends on future events. In a truly efficient prediction market, 
the price of a contract will be the best predictor of the related event.
This program runs a simulation of such a market giving the user the 
possibility of studying this kind of system under different circumstances.

    Usage:

    python3 usage: run.py [-h] [-n NUM_AGENTS] [-i NUM_ITERATIONS] [-r RISK_FACTOR]
              [-t TRUST] [-e NUM_EVIDENCE] [-f FRACTION_RECEIVING_EVIDENCE]
              [-x EXTRA_TIME] [-w WEALTH]

"""

import random
import heapq
import argparse
import pandas as pd      
import matplotlib.pyplot as plt
import time
from god import God
from market import Market

parser = argparse.ArgumentParser(description='Parameters of the Prediction Market simulation.')
parser.add_argument('-n', metavar="num_agents",         default=50,     type=int,   help='The number of agents in the market (default: 50).')
parser.add_argument('-i', metavar="num_iterations",     default=50,     type=int,   help='The number of iterations of the market (default: 50).')
parser.add_argument('-r', metavar="risk_factor",        default=0.5,    type=float, help='Determines the number of contracts the agent will buy, [e.g. Buy = (Belief - Price) * 100 * Risk] (Default: 0.5).')
parser.add_argument('-t', metavar="trust",              default=0.9,    type=float, help='Determines how much the agents trust the market price as an indicator of probability (Default: 0.9).')
parser.add_argument('-e', metavar="num_evidence",       default=20,     type=int,   help='The number of evidences provided to the agents (default: 20).')
parser.add_argument('-f', metavar="receiving_evidence", default=0.1,    type=float, help='Determines how many agents receive pieces of evidence (Default: 0.1).')
parser.add_argument('-x', metavar="extra_time",         default=0.33,   type=float, help='Determines how much time the agents keep on trading after all the evidence has been provided (Default: 0.33).')
parser.add_argument('-w', metavar="wealth",             default=100,    type=int,   help='Units of currency every agent is initialized with (Default: 100).')

args = parser.parse_args()

N_AGENTS                             = args.n           # Number of the agents particecipating in the system.
MAX_ITER                             = args.i           # Number of cycles of the market, every agent performs an action in each cycle.
N_EVIDENCE                           = args.e           # How many times a piece of information is shared with a percentage of the population.
FRACTION_RECEIVING_EVIDENCE          = args.f           # Percentage of agents who receive information when it is introduced.
FRACTION_EXTRA_TIME                  = args.x           # Fraction of the total number of cycles, determines how many cycles the agents keep on trading after the last piece of information has been provided.
RISK_FACTOR                          = args.r           # Used to determine how many contracts an agent buys when it expects to profit. [Buy = (Belief - Price) * 100 * Risk]
TRUST                                = args.t           # How much the agents trust the market price as an indicator of probability of the event.
WEALTH                               = args.w           # Units of currency every agent is initialized with, it's exchanged to buy contracts.
EVIDENCE_TIME = int((1-FRACTION_EXTRA_TIME)*MAX_ITER)   # Number of cycles the agents keep on trading after all the evidence has been provided.

    
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
        
def get_bayesian_update_factor(old_price, new_price):
    """TODO: discuss math behind this."""
    return (old_price*(1-new_price))/(new_price*(1-old_price))
    
def learn_from_market(market):
    """Updates the beliefs of the agents."""
    if market.market_price == None or market.old_market_price == None:
        return
    bayes_factor = get_bayesian_update_factor(market.old_market_price, market.market_price)
    for i in range(0, N_AGENTS):
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
    plt.legend(['Market Price', 'True Bayesian Probability'])
    plt.xlabel("Iterations (Market Cycles)")
    plt.ylabel("Price")
    fig.canvas.draw()
    plt.pause(1e-17)
    time.sleep(0.00001)



def main():

    # Exit the program if user inputs invalid arguments.
    if (RISK_FACTOR <= 0.0):
        print("Error: Invalid Argument for RISK_FACTOR: must be more than 0.0.")
        exit()
    if (TRUST >= 1.0 or TRUST <= 0.0):
        print("Error: Invalid Argument for TRUST: must be in range [0.0, 1.0].")
        exit()

    # We use this object to distribute evidence, 
    # and maintain the complete bayesian probability.
    the_almighty = God(0.6, 1-0.6, N_AGENTS)
    
    iters_per_evidence = int(EVIDENCE_TIME/N_EVIDENCE)
    
    print("Creating {} agents...\n".format(N_AGENTS))
    market = Market(N_AGENTS, RISK_FACTOR, TRUST, WEALTH)
    # data = pd.DataFrame(columns=['iter', 'agent_id', 'belief', 'wealth', 'n_for', 'n_against', 'market_price'])
    price_history = []
    god_history = []

    bids_against = []
    heapq.heapify(bids_against)
    bids_for = []
    heapq.heapify(bids_against)

    plt.ion()
    fig = plt.figure(figsize=(16,8))
    ax = plt.gca()
    plt.grid()
    

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
        
        print("Iter: ", i, "\tMarket Price: ", market.market_price)
        price_history.append(market.market_price)
        god_history.append(the_almighty.belief)

        plot_dynamic(range(i+1), price_history, fig, ax, color="blue")
        plot_dynamic(range(i+1), god_history, fig, ax, color="orange")
        plt.draw()
        ### TODO: Add difference between the values area graph

    print("God's Belief: ", the_almighty.belief)
        
    #all_beliefs = [market.all_agents[i].belief for i in range(0,N_AGENTS)]
    #average = sum(all_beliefs) / len(all_beliefs)
    #print("Average Belief: ", average)
    
    print("Final Market Price: ", market.market_price)
    
    print("\nAgent Summary:")
    
    for a in market.all_agents:
        print("Agent ID: ", a.i_d, "\tBelief: ", "{0:.2f}".format(a.belief), "\tFor: ", a.n_contracts_for, "\tAgainst: ", a.n_contracts_against, "\tWealth: ", "{0:.2f}".format(a.wealth))
    
    plt.waitforbuttonpress()


if __name__ == "__main__":
    main()
    
    
