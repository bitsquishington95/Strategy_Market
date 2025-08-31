"""
Models for the CEO training program.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class SkillLevel(str, Enum):
    """Skill levels for CEO competencies"""
    NOVICE = "novice"
    DEVELOPING = "developing"
    PROFICIENT = "proficient"
    ADVANCED = "advanced"
    EXPERT = "expert"


class PillarSkill(BaseModel):
    """Skill assessment for a specific CEO pillar"""
    level: SkillLevel = Field(default=SkillLevel.NOVICE)
    strengths: List[str] = Field(default_factory=list)
    growth_areas: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class TraineeProfile(BaseModel):
    """Profile for a CEO training program participant"""
    id: str
    name: str
    current_role: str
    target_role: str
    industry: Optional[str] = None
    years_experience: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Skill assessment across the four pillars
    strategic_philosophy: PillarSkill = Field(default_factory=PillarSkill)
    leadership_style: PillarSkill = Field(default_factory=PillarSkill)
    operational_cadence: PillarSkill = Field(default_factory=PillarSkill)
    personal_ethos: PillarSkill = Field(default_factory=PillarSkill)
    
    # Preferred learning styles and CEO role models
    learning_preferences: List[str] = Field(default_factory=list)
    role_models: List[str] = Field(default_factory=list)
    
    # Training progress
    completed_modules: List[str] = Field(default_factory=list)
    completed_scenarios: List[str] = Field(default_factory=list)


class LearningResource(BaseModel):
    """Learning resource for CEO training"""
    id: str
    title: str
    resource_type: str  # book, article, video, exercise, etc.
    pillar: str  # strategic_philosophy, leadership_style, operational_cadence, personal_ethos
    description: str
    url: Optional[str] = None
    ceo_examples: List[str] = Field(default_factory=list)  # CEOs who exemplify this concept
    difficulty: SkillLevel = Field(default=SkillLevel.NOVICE)
    estimated_time_minutes: int = 0


class TrainingScenario(BaseModel):
    """Scenario-based training exercise"""
    id: str
    title: str
    situation: str
    context: str
    pillar: str
    difficulty: SkillLevel = Field(default=SkillLevel.NOVICE)
    
    # CEO examples and approaches
    ceo_approaches: Dict[str, str] = Field(default_factory=dict)  # CEO name -> approach
    principles: List[str] = Field(default_factory=list)
    
    # Evaluation criteria
    evaluation_criteria: List[str] = Field(default_factory=list)


class TrainingModule(BaseModel):
    """A structured training module focused on a specific aspect of CEO leadership"""
    id: str
    title: str
    description: str
    pillar: str
    skill_level: SkillLevel = Field(default=SkillLevel.NOVICE)
    
    # Content
    learning_objectives: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)  # IDs of learning resources
    scenarios: List[str] = Field(default_factory=list)  # IDs of training scenarios
    
    # Metadata
    estimated_time_hours: float = 0
    prerequisites: List[str] = Field(default_factory=list)  # IDs of prerequisite modules


class TrainingPlan(BaseModel):
    """Personalized training plan for a trainee"""
    trainee_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Modules in sequence
    modules: List[str] = Field(default_factory=list)  # IDs of training modules
    
    # Progress tracking
    current_module_index: int = 0
    completion_percentage: float = 0
    
    # Personalization
    focus_areas: List[str] = Field(default_factory=list)
    role_model_influences: List[str] = Field(default_factory=list)


class ScenarioSubmission(BaseModel):
    """Trainee's submission for a training scenario"""
    trainee_id: str
    scenario_id: str
    submission_date: datetime = Field(default_factory=datetime.now)
    
    # Submission content
    approach: str
    principles_applied: List[str] = Field(default_factory=list)
    
    # Feedback
    feedback: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    
    # Similar CEOs based on approach
    similar_ceos: List[Dict[str, float]] = Field(default_factory=list)  # List of {ceo_name: similarity_score}


class ProgressReport(BaseModel):
    """Progress report for a trainee"""
    trainee_id: str
    report_date: datetime = Field(default_factory=datetime.now)
    
    # Overall progress
    modules_completed: int = 0
    scenarios_completed: int = 0
    total_modules: int = 0
    total_scenarios: int = 0
    
    # Skill development
    skill_levels: Dict[str, SkillLevel] = Field(default_factory=dict)
    
    # Growth trajectory
    strengths: List[str] = Field(default_factory=list)
    focus_areas: List[str] = Field(default_factory=list)
    
    # CEO archetype and similarities
    archetype: Optional[str] = None
    similar_ceos: List[Dict[str, float]] = Field(default_factory=list)  # List of {ceo_name: similarity_score}
