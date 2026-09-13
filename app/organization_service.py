from organization_planner import plan_by_year
from organization_executor import execute_plan


def get_organization_preview():
    """
    Generate a read-only organization preview.
    """

    plan = plan_by_year()

    summary = {
        "photos": len(plan),
        "safe": sum(
            item["status"] == "SAFE"
            for item in plan
        ),
        "conflicts": sum(
            item["status"] == "CONFLICT"
            for item in plan
        ),
        "already_organized": sum(
            item["status"] == "ALREADY_ORGANIZED"
            for item in plan
        ),
        "missing_source": sum(
            item["status"] == "MISSING_SOURCE"
            for item in plan
        ),
    }

    return {
        "summary": summary,
        "plan": plan,
    }


def execute_organization(confirm=False):
    """
    Generate the latest plan and execute it.

    A fresh plan is generated immediately before execution.
    This prevents an old preview from being blindly executed
    after files have changed.
    """

    plan = plan_by_year()

    results = execute_plan(
        plan,
        confirm=confirm,
    )

    return {
        "count": len(results),
        "results": results,
    }