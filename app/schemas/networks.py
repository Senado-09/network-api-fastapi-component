from pydantic import BaseModel


class AssignUserRequest(BaseModel):
    user_id: str
    parranage_code: str


class CreateCommercialNetworkRequest(BaseModel):
    commercial_id: str


class CalculatePositionRequest(BaseModel):
    network_id: str
    plan_type: str


class GenerationPositionResponse(BaseModel):
    generation: int
    position_in_generation: int
