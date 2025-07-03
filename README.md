## Summary
This project explores a simulated warehouse environment where multiple autonomous robots learn to pick up and deliver different types of packages to their correct drop-off zones using reinforcement learning. 
Through repeated interaction, the robots learn to identify package types, navigate the space efficiently, and coordinate actions to complete deliveries accurately. 
The goal is to model intelligent behavior in a dynamic logistics setting without relying on predefined rules or supervision.

## Module Specs
- Ray RLlib for training, orchestration and parallelization 
- PyGame for visualizations
## TODO
- [x] Implement Game Logic and Visuals
- [ ] Adapt to Reinforcement Learning
- [ ] Train and Visualize Results

## Reward - Penalty Mapping
| Action                                                               |Reward|Penalty|Value|
|----------------------------------------------------------------------|-|-|-|
| Robot collides with robot                                            ||x|-10
| Robot collides with wall or obstacle                                 ||x|-8
| Robot collects item                                                  |x||+5
| Robot leaves pickup area                                             |x||+2
| Robot takes too long to leave the pickup area when item in inventory ||x|-3
| Robot tries to collect item with item in inventory                   ||x|-5
| Robot delivers item to correct dropzone                              |x||+10
| Robot tries to deliver to the wrong dropzone                         ||x|-6
| Robot reenters pickup area when no item in inventory                 |x||+2
| Robot takes too long to reenter the pickup area when no item         ||x|-3


## Implementation Steps
- [ ] Observe state
- [ ] Take action
- [ ] Calculated rewards
- [ ] Observe new state
- [ ]