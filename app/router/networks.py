from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
from app.config import get_db
from networks.app.router.utils import (
    assign_user_to_network,
    calculate_generation_and_position,
    create_and_add_commercial_to_network,
    get_user_network_tree
)
from networks.app.schemas.networks import (
    AssignUserRequest,
    CreateCommercialNetworkRequest,
    CalculatePositionRequest,
    GenerationPositionResponse
)

router = APIRouter(prefix="/network", tags=["Network"])


# Assign a user to an existing network using a referral code or create a new one if necessary.
@router.post(
    "/assign-user",
    summary="Assign a user to a network",
    description="Assign a user to an existing network using a referral code or create a new one if necessary."
)
def assign_user(
    request: AssignUserRequest,
    db: Session = Depends(get_db)
):
    try:
        success, message = assign_user_to_network(
            user_id=request.user_id,
            parranage_code=request.parranage_code,
            db=db
        )
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"message": message}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Creates a new network and registers the commercial as its first member.
@router.post(
    "/create-commercial-network",
    summary="Create a network for a commercial",
    description="Creates a new network and registers the commercial as its first member."
)
def create_network_for_commercial(
    request: CreateCommercialNetworkRequest,
    db: Session = Depends(get_db)
):
    success, message = create_and_add_commercial_to_network(
        commercial_id=request.commercial_id,
        db=db
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {
        "message": message
        }

# Determines the generation and position in the network based on its plan type.
@router.post(
    "/calculate-position",
    summary="Calculate generation and position in network",
    description="Determines the generation and position in the network based on its plan type."
)
def calculate_position(
    request: CalculatePositionRequest,
    db: Session = Depends(get_db)
) -> GenerationPositionResponse:
    try:
        generation, position = calculate_generation_and_position(
            db=db,
            network_id=request.network_id,
            plan_type=request.plan_type
        )

        return GenerationPositionResponse(
            generation=generation,
            position_in_generation=position
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Returns the hierarchical structure of the network for the given user.
@router.get(
    "/users/{user_id}/network-tree",
    summary="Get a user's network tree",
    description="Returns the hierarchical structure of the network for the given user."
)
def get_user_tree(
    user_id: str,
    db: Session = Depends(get_db)
):
    return get_user_network_tree(user_id, db)
