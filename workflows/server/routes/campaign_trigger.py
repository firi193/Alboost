from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from workflows.agent_orchestration import ContentMarketingWorkflow

router = APIRouter()

@router.post("/campaign-request")
async def campaign_request(request: Request):
    body = await request.json()

    campaign_goal = body.get("goal")
    campaign_type = body.get("projectType")

    if not campaign_goal or not campaign_type:
        return JSONResponse(
            {"error": "Missing required fields"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    workflow = ContentMarketingWorkflow()
    workflow.start_workflow(campaign_goal)

    # Get the strategy from the strategist agent
    strategy_result = workflow.get_strategy_result()

    return JSONResponse(
        {
            "status": "success",
            "strategy": strategy_result or "No strategy returned.",
            "tweets": [],  # Add tweet retrieval logic later if needed
        },
        status_code=status.HTTP_200_OK
    )
