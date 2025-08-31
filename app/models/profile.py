from pydantic import BaseModel
from typing import List


class StrategicPhilosophy(BaseModel):
    core_ideology: str
    market_positioning: str
    innovation_engine: str
    competitive_stance: str
    risk_profile: str


class Leadership(BaseModel):
    hiring_philosophy: str
    cultural_architecture: str
    motivation_incentives: str
    communication_style: str
    talent_management: str


class OperationalCadence(BaseModel):
    meeting_culture: str
    decision_making_process: str
    key_metrics: str
    focus_prioritization: str
    accountability_framework: str


class PersonalEthos(BaseModel):
    core_principles: str
    work_ethic: str
    learning_adaptability: str
    resilience_mechanism: str


class CEOProfile(BaseModel):
    name: str
    strategic_philosophy: StrategicPhilosophy
    leadership: Leadership
    operational_cadence: OperationalCadence
    personal_ethos: PersonalEthos


class SituationalResponse(BaseModel):
    ceo: str
    tags: List[str]
    title: str
    response: str


class RepositoryData(BaseModel):
    ceos: List[CEOProfile]
    situations: List[SituationalResponse]


