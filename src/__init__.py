"""
Multi-Touch Marketing Attribution & ROI Analytics Package
Author: Antigravity AI & Adarsh
"""

from .data_loader import load_and_preprocess_data
from .attribution_models import (
    calculate_first_touch,
    calculate_last_touch,
    calculate_linear,
    calculate_time_decay,
    calculate_position_based,
    calculate_markov_chain_attribution,
    apply_all_attribution_models
)
from .roi_analytics import (
    calculate_channel_performance,
    calculate_journey_path_performance,
    generate_budget_optimization_recommendations
)
from .visualizations import (
    plot_attribution_model_comparison,
    plot_channel_roas_vs_spend,
    plot_markov_transition_heatmap,
    plot_budget_optimization_waterfall
)
