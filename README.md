# Group B16 - Prediction Market Simulation: Design of Multi-Agent Systems Project
In prediction (or Information) markets participants trade in contracts whose payoff depends on future events. In a truly efficient prediction market, the price of a contract will be the best predictor of the related event.

## Instructions
Fulfill requirements:
```
pip3 install numpy matplotlib
```
Run default parameters (50 agents, 100 iterations):
```
python3 run.py
```
To manually input parameters:
```
python3 run.py [-h] [-n NUM_AGENTS] [-i NUM_ITERATIONS] [-r RISK_FACTOR]
              [-t TRUST] [-e NUM_EVIDENCE] [-f FRACTION_RECEIVING_EVIDENCE]
              [-x EXTRA_TIME] [-w WEALTH]
```
Example: 
```
python3 run.py -n 100 -i 50
```
