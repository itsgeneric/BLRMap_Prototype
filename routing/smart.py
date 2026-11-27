"""
The two-wheeler planner: prefer inner roads, but never at the price of a long way round.

The road-class table (core/config.py) makes inner roads cheap and main roads expensive. On its own that has no limit: a
trip could become much longer just to stay off a main road, and so could a trip avoiding a traffic jam. A rider loses
more time on that long way than they save.

So every Dynamic route has a DETOUR BUDGET, measured against the most direct legal route for the same trip:

    budget = max(direct x MAX_DETOUR_RATIO, direct + DETOUR_SLACK_M)

The planner tries the full inner-road preference first. If that route is over budget it weakens the preference step by
step (PREFERENCE_LEVELS) until a route fits. If even a route with no preference is over budget, that can only be because
it is avoiding traffic, and the direct route is used: going through the jam beats the long way round.

Guarantee: a Dynamic route is never longer than the budget. Reported incidents (crash, flood ...) are part of the
direct route too, so avoiding one is never cut off by the budget.
"""
from core.config import MAX_DETOUR_RATIO, DETOUR_SLACK_M, PREFERENCE_LEVELS
from routing.snapping import plan_route


def blend_penalties(penalties, level):
    """The road-class table weakened towards "every road costs its length": level 1 = full table, 0 = no preference."""
    return {
        key: value if str(key).startswith('_') else 1.0 + level * (value - 1.0)
        for key, value in penalties.items()
    }


def detour_budget_m(direct_m):
    return max(direct_m * MAX_DETOUR_RATIO, direct_m + DETOUR_SLACK_M)


def _uses(plan, congested_nodes):
    nodes = plan["nodes"]
    return any(a in congested_nodes and b in congested_nodes for a, b in zip(nodes, nodes[1:]))


def plan_smart(G, graph_mgr, origins, destinations, penalties, congested_nodes=None, incident_nodes=None,
               landmarks=None, blacklist=None):
    """
    Same inputs and result as snapping.plan_route(mode='dynamic'), plus:
        preference_level     1.0 = full inner-road preference ... 0.0 = the most direct route
        direct_distance_m    length of the most direct route, which the budget is measured against
        through_traffic      True when the chosen route passes through reported congestion
    """
    common = dict(incident_nodes=incident_nodes, blacklist=blacklist, landmarks=landmarks)

    def plan(level, jams):
        return plan_route(G, graph_mgr, "dynamic", origins, destinations,
                          penalties=blend_penalties(penalties, level), congested_nodes=jams, **common)

    direct = plan(0.0, None)
    budget = detour_budget_m(direct["distance_m"])

    chosen, level_used = direct, 0.0
    for level in PREFERENCE_LEVELS:
        candidate = direct if level == 0.0 and not congested_nodes else plan(level, congested_nodes)
        if candidate["distance_m"] <= budget:
            chosen, level_used = candidate, level
            break

    return {
        **chosen,
        "preference_level": level_used,
        "direct_distance_m": direct["distance_m"],
        "through_traffic": bool(congested_nodes) and _uses(chosen, congested_nodes),
    }
