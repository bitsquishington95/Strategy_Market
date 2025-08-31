# app/models/temporal.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ProfileFact(BaseModel):
    pillar: str
    field: str
    value: str
    confidence: Optional[float] = None
    citations: Optional[List[str]] = None

class CEOProfileVersionOut(BaseModel):
    id: int
    name: str
    company: str
    industry: str
    versions: List[Dict[str, Any]]

class CEOCardOut(BaseModel):
    id: int
    name: str
    company: str
    industry: str
    eras: List[str]

class SituationOut(BaseModel):
    id: int
    ceo_id: int
    tags: List[str]
    title: str
    situation: str
    approach: str
    principles: List[str]
    outcome: Optional[str]
    occurred_on: Optional[str]
    applies_version_id: Optional[int]
    confidence: Optional[float]
    citations: Optional[List[str]]