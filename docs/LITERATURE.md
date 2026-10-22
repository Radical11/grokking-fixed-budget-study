# Prior work and originality statement

Search performed during planning on 13 October 2026. Exa searches covered 85 result entries across timing, distributions, fixed-budget training and restart strategies; entries overlap, so this is not 85 unique papers. No exact match was identified for independent from-scratch restart allocation versus one uninterrupted grokking run under equal aggregate optimizer updates. This is a limited search, not proof of an unpublished question.

1. Power et al., 2022: **Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets**. Original delayed generalization phenomenon and data-size dependence. https://arxiv.org/abs/2201.02177
2. Truong et al., 2026: **First-Passage Prediction of Grokking Delay: A Calibrated Law under AdamW with Causal Validation**. Closely related timing prediction; our project does not claim to introduce random event-time framing. https://arxiv.org/abs/2605.18845
3. Streeter, Golovin and Smith, 2007: **Restart Schedules for Ensembles of Problem Instances**. Established restart-distribution foundation; the probability identity is not a new theorem. https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf
4. Kataria, 2026: **Quantifying the Memorization-to-Generalization Transition: Scaling Laws and Phase Structure in Grokking**. Related hyperparameter timing/compute analysis. https://arxiv.org/abs/2609.10657
5. Ootani, 2026: **Grokking Is Conditional and Fragile: A Fully-Tractable, Multi-Seed Study at 12K Parameters**. Related seed variability and generalization-rate research. https://arxiv.org/abs/2607.05104

An additional directly overlapping title, **Grokking time is a random variable and attention sets its variance**, appeared on Recensorium (https://recensorium.com/papers/rcs_ppr_nph4tfvnn3t10xvxpbbj). The page identifies an AI-agent submission and platform reviews; treat it as a related online manuscript, not established conventional peer-reviewed evidence. It is another reason not to claim the broad time-as-random-variable idea as new.

Suitable claim: “We conduct a controlled, syllabus-based empirical study of whether allocating a finite training budget across independent initializations improves the probability of generalization in a small modular-addition network.”

Unsuitable claim: “We are the first to discover that grokking time is stochastic” or “we invented restart theory.”
