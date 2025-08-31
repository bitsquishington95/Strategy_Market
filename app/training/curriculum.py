"""
Curriculum generator for the CEO training program.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import sys
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.training.models import (
    TraineeProfile, TrainingModule, LearningResource, 
    TrainingScenario, TrainingPlan, SkillLevel
)
from app.engine.embeddings import get_embedding_engine

# Try to import repository
try:
    from app.repository.store import Repository, load_repository
    REPO_AVAILABLE = True
except ImportError:
    logger.warning("Repository module not available")
    REPO_AVAILABLE = False

# Base training modules by pillar and skill level
BASE_MODULES = {
    "strategic_philosophy": {
        SkillLevel.NOVICE: [
            {
                "id": "sp_foundations",
                "title": "Strategic Thinking Foundations",
                "description": "Learn the fundamentals of strategic thinking and vision setting",
                "learning_objectives": [
                    "Understand the difference between tactics and strategy",
                    "Learn how to analyze competitive landscapes",
                    "Develop a basic strategic framework",
                    "Practice articulating a vision statement"
                ],
                "estimated_time_hours": 10
            },
            {
                "id": "sp_market_analysis",
                "title": "Market Analysis Fundamentals",
                "description": "Learn how to analyze markets and identify opportunities",
                "learning_objectives": [
                    "Understand market segmentation",
                    "Learn to identify customer needs and pain points",
                    "Analyze competitive positioning",
                    "Identify potential market opportunities"
                ],
                "estimated_time_hours": 8
            }
        ],
        SkillLevel.DEVELOPING: [
            {
                "id": "sp_competitive_advantage",
                "title": "Building Sustainable Competitive Advantage",
                "description": "Learn how to create and maintain competitive advantages",
                "learning_objectives": [
                    "Understand different types of competitive advantages",
                    "Learn how to identify your organization's unique strengths",
                    "Develop strategies to protect and enhance competitive advantages",
                    "Analyze case studies of successful competitive strategies"
                ],
                "estimated_time_hours": 12
            },
            {
                "id": "sp_strategic_planning",
                "title": "Strategic Planning Process",
                "description": "Learn a structured approach to strategic planning",
                "learning_objectives": [
                    "Understand the components of a strategic plan",
                    "Learn how to set strategic objectives and key results",
                    "Develop a process for strategic reviews and adjustments",
                    "Practice creating a strategic plan"
                ],
                "estimated_time_hours": 15
            }
        ],
        SkillLevel.PROFICIENT: [
            {
                "id": "sp_disruption",
                "title": "Disruptive Strategy and Innovation",
                "description": "Learn how to create disruptive strategies and foster innovation",
                "learning_objectives": [
                    "Understand the principles of disruptive innovation",
                    "Learn how to identify potential disruptions in your industry",
                    "Develop an innovation framework for your organization",
                    "Create a plan to foster a culture of innovation"
                ],
                "estimated_time_hours": 18
            },
            {
                "id": "sp_platform_thinking",
                "title": "Platform Strategy and Ecosystems",
                "description": "Learn how to develop platform strategies and build ecosystems",
                "learning_objectives": [
                    "Understand platform business models and network effects",
                    "Learn how to identify platform opportunities",
                    "Develop strategies for building and growing ecosystems",
                    "Analyze successful platform companies and their strategies"
                ],
                "estimated_time_hours": 15
            }
        ],
        SkillLevel.ADVANCED: [
            {
                "id": "sp_global_strategy",
                "title": "Global Strategy and Expansion",
                "description": "Learn how to develop and execute global strategies",
                "learning_objectives": [
                    "Understand global market dynamics and entry strategies",
                    "Learn how to adapt strategies for different markets and cultures",
                    "Develop approaches for managing global operations",
                    "Create a framework for global expansion"
                ],
                "estimated_time_hours": 20
            },
            {
                "id": "sp_strategic_transformation",
                "title": "Leading Strategic Transformation",
                "description": "Learn how to lead major strategic transformations",
                "learning_objectives": [
                    "Understand the dynamics of organizational transformation",
                    "Learn how to identify when transformation is needed",
                    "Develop approaches for managing resistance and building momentum",
                    "Create a transformation roadmap and communication plan"
                ],
                "estimated_time_hours": 25
            }
        ],
        SkillLevel.EXPERT: [
            {
                "id": "sp_industry_creation",
                "title": "Industry Creation and Market Making",
                "description": "Learn how to create new industries and markets",
                "learning_objectives": [
                    "Understand the principles of market creation",
                    "Learn how to identify opportunities for new industries",
                    "Develop strategies for overcoming adoption barriers",
                    "Create a framework for industry creation"
                ],
                "estimated_time_hours": 30
            },
            {
                "id": "sp_strategic_foresight",
                "title": "Strategic Foresight and Future-Back Planning",
                "description": "Learn advanced methods for anticipating the future and planning backward",
                "learning_objectives": [
                    "Understand strategic foresight methodologies",
                    "Learn how to identify weak signals and emerging trends",
                    "Develop scenario planning capabilities",
                    "Create a future-back strategic planning process"
                ],
                "estimated_time_hours": 25
            }
        ]
    },
    "leadership_style": {
        SkillLevel.NOVICE: [
            {
                "id": "ls_foundations",
                "title": "Leadership Fundamentals",
                "description": "Learn the foundations of effective leadership",
                "learning_objectives": [
                    "Understand different leadership styles and their applications",
                    "Learn basic principles of team motivation",
                    "Develop fundamental communication skills",
                    "Practice giving effective feedback"
                ],
                "estimated_time_hours": 10
            },
            {
                "id": "ls_team_building",
                "title": "Building Effective Teams",
                "description": "Learn how to build and develop high-performing teams",
                "learning_objectives": [
                    "Understand team dynamics and development stages",
                    "Learn principles of effective team composition",
                    "Develop approaches for building trust and psychological safety",
                    "Practice team-building exercises and activities"
                ],
                "estimated_time_hours": 12
            }
        ],
        SkillLevel.DEVELOPING: [
            {
                "id": "ls_coaching",
                "title": "Coaching and Developing Others",
                "description": "Learn how to coach and develop team members",
                "learning_objectives": [
                    "Understand coaching principles and frameworks",
                    "Learn how to conduct effective development conversations",
                    "Develop skills for identifying development needs",
                    "Practice coaching conversations"
                ],
                "estimated_time_hours": 15
            },
            {
                "id": "ls_hiring",
                "title": "Strategic Hiring and Talent Management",
                "description": "Learn how to hire and manage talent strategically",
                "learning_objectives": [
                    "Understand principles of strategic workforce planning",
                    "Learn how to create effective hiring processes",
                    "Develop approaches for assessing cultural fit and potential",
                    "Create a talent management framework"
                ],
                "estimated_time_hours": 12
            }
        ],
        SkillLevel.PROFICIENT: [
            {
                "id": "ls_culture",
                "title": "Building and Shaping Culture",
                "description": "Learn how to intentionally build and shape organizational culture",
                "learning_objectives": [
                    "Understand the components and dynamics of organizational culture",
                    "Learn how to assess current culture and identify gaps",
                    "Develop approaches for cultural change and reinforcement",
                    "Create a culture-building plan"
                ],
                "estimated_time_hours": 18
            },
            {
                "id": "ls_influence",
                "title": "Influence and Stakeholder Management",
                "description": "Learn how to influence across and beyond the organization",
                "learning_objectives": [
                    "Understand principles of influence and persuasion",
                    "Learn how to map and analyze stakeholders",
                    "Develop strategies for building coalitions and managing resistance",
                    "Practice influence techniques in different scenarios"
                ],
                "estimated_time_hours": 15
            }
        ],
        SkillLevel.ADVANCED: [
            {
                "id": "ls_executive_presence",
                "title": "Executive Presence and Communication",
                "description": "Develop advanced executive presence and communication skills",
                "learning_objectives": [
                    "Understand the components of executive presence",
                    "Learn techniques for high-stakes communications",
                    "Develop skills for communicating vision and strategy",
                    "Practice executive communications in various contexts"
                ],
                "estimated_time_hours": 20
            },
            {
                "id": "ls_succession",
                "title": "Succession Planning and Leadership Development",
                "description": "Learn how to build leadership pipelines and plan for succession",
                "learning_objectives": [
                    "Understand principles of succession planning",
                    "Learn how to identify and develop high-potential talent",
                    "Develop approaches for creating leadership development programs",
                    "Create a succession planning framework"
                ],
                "estimated_time_hours": 18
            }
        ],
        SkillLevel.EXPERT: [
            {
                "id": "ls_transformational",
                "title": "Transformational Leadership",
                "description": "Learn how to lead transformational change and inspire organizations",
                "learning_objectives": [
                    "Understand principles of transformational leadership",
                    "Learn how to create and communicate compelling visions",
                    "Develop approaches for leading through uncertainty and complexity",
                    "Create a personal transformational leadership framework"
                ],
                "estimated_time_hours": 25
            },
            {
                "id": "ls_legacy",
                "title": "Building Leadership Legacy",
                "description": "Learn how to create lasting impact and develop future leaders",
                "learning_objectives": [
                    "Understand principles of leadership legacy",
                    "Learn how to institutionalize values and principles",
                    "Develop approaches for creating leadership factories",
                    "Create a legacy plan that extends beyond your tenure"
                ],
                "estimated_time_hours": 20
            }
        ]
    },
    "operational_cadence": {
        SkillLevel.NOVICE: [
            {
                "id": "oc_foundations",
                "title": "Operational Excellence Foundations",
                "description": "Learn the fundamentals of operational excellence",
                "learning_objectives": [
                    "Understand principles of effective operations",
                    "Learn basic project and process management",
                    "Develop skills for setting priorities and managing time",
                    "Practice creating effective meeting agendas and action plans"
                ],
                "estimated_time_hours": 10
            },
            {
                "id": "oc_metrics",
                "title": "Metrics and Performance Management",
                "description": "Learn how to use metrics to drive performance",
                "learning_objectives": [
                    "Understand different types of metrics and their uses",
                    "Learn how to set effective goals and key performance indicators",
                    "Develop skills for tracking and reviewing performance",
                    "Practice creating performance dashboards"
                ],
                "estimated_time_hours": 8
            }
        ],
        SkillLevel.DEVELOPING: [
            {
                "id": "oc_decision",
                "title": "Effective Decision-Making",
                "description": "Learn frameworks and processes for making better decisions",
                "learning_objectives": [
                    "Understand different decision-making frameworks",
                    "Learn how to gather and analyze relevant information",
                    "Develop approaches for involving others in decisions",
                    "Practice making decisions in various scenarios"
                ],
                "estimated_time_hours": 12
            },
            {
                "id": "oc_execution",
                "title": "Execution Excellence",
                "description": "Learn how to consistently execute plans and initiatives",
                "learning_objectives": [
                    "Understand principles of effective execution",
                    "Learn how to create accountability systems",
                    "Develop approaches for removing obstacles and solving problems",
                    "Create an execution framework for your organization"
                ],
                "estimated_time_hours": 15
            }
        ],
        SkillLevel.PROFICIENT: [
            {
                "id": "oc_meeting_systems",
                "title": "Designing Effective Meeting Systems",
                "description": "Learn how to create meeting systems that drive results",
                "learning_objectives": [
                    "Understand different meeting types and their purposes",
                    "Learn how to design an organizational meeting rhythm",
                    "Develop skills for facilitating different types of meetings",
                    "Create a meeting system for your organization"
                ],
                "estimated_time_hours": 10
            },
            {
                "id": "oc_resource_allocation",
                "title": "Strategic Resource Allocation",
                "description": "Learn how to allocate resources to maximize impact",
                "learning_objectives": [
                    "Understand principles of effective resource allocation",
                    "Learn how to evaluate competing priorities",
                    "Develop approaches for portfolio management",
                    "Create a resource allocation process"
                ],
                "estimated_time_hours": 15
            }
        ],
        SkillLevel.ADVANCED: [
            {
                "id": "oc_scaling",
                "title": "Scaling Operations and Systems",
                "description": "Learn how to scale operations while maintaining quality",
                "learning_objectives": [
                    "Understand challenges and principles of scaling",
                    "Learn how to design scalable processes and systems",
                    "Develop approaches for maintaining culture during scaling",
                    "Create a scaling playbook for your organization"
                ],
                "estimated_time_hours": 20
            },
            {
                "id": "oc_data_driven",
                "title": "Building a Data-Driven Organization",
                "description": "Learn how to use data to drive decisions and performance",
                "learning_objectives": [
                    "Understand principles of data-driven management",
                    "Learn how to identify and track leading indicators",
                    "Develop approaches for creating a data culture",
                    "Create a data strategy for your organization"
                ],
                "estimated_time_hours": 18
            }
        ],
        SkillLevel.EXPERT: [
            {
                "id": "oc_organizational_design",
                "title": "Strategic Organizational Design",
                "description": "Learn how to design organizations that execute strategy effectively",
                "learning_objectives": [
                    "Understand principles of organizational design",
                    "Learn how to align structure with strategy",
                    "Develop approaches for managing organizational complexity",
                    "Create an organizational design framework"
                ],
                "estimated_time_hours": 25
            },
            {
                "id": "oc_operating_system",
                "title": "Building an Organizational Operating System",
                "description": "Learn how to create a comprehensive operating system for your organization",
                "learning_objectives": [
                    "Understand the components of an organizational operating system",
                    "Learn how to integrate planning, execution, and learning cycles",
                    "Develop approaches for continuous improvement",
                    "Create an operating system blueprint for your organization"
                ],
                "estimated_time_hours": 30
            }
        ]
    },
    "personal_ethos": {
        SkillLevel.NOVICE: [
            {
                "id": "pe_foundations",
                "title": "Personal Leadership Foundations",
                "description": "Learn the foundations of personal leadership",
                "learning_objectives": [
                    "Understand the importance of self-awareness in leadership",
                    "Learn how to identify your values and principles",
                    "Develop basic reflection and mindfulness practices",
                    "Create a personal leadership statement"
                ],
                "estimated_time_hours": 8
            },
            {
                "id": "pe_resilience",
                "title": "Building Personal Resilience",
                "description": "Learn how to build resilience and manage stress",
                "learning_objectives": [
                    "Understand the science of stress and resilience",
                    "Learn techniques for managing stress and building resilience",
                    "Develop a personal resilience practice",
                    "Create strategies for maintaining balance"
                ],
                "estimated_time_hours": 10
            }
        ],
        SkillLevel.DEVELOPING: [
            {
                "id": "pe_learning",
                "title": "Continuous Learning and Growth",
                "description": "Learn how to develop a continuous learning practice",
                "learning_objectives": [
                    "Understand principles of adult learning and skill development",
                    "Learn how to create effective learning goals and plans",
                    "Develop approaches for learning from experience",
                    "Create a personal learning system"
                ],
                "estimated_time_hours": 12
            },
            {
                "id": "pe_feedback",
                "title": "Seeking and Using Feedback",
                "description": "Learn how to seek and use feedback for personal growth",
                "learning_objectives": [
                    "Understand the importance of feedback for leadership development",
                    "Learn how to seek feedback effectively",
                    "Develop skills for processing and acting on feedback",
                    "Create a personal feedback system"
                ],
                "estimated_time_hours": 10
            }
        ],
        SkillLevel.PROFICIENT: [
            {
                "id": "pe_authentic",
                "title": "Authentic Leadership",
                "description": "Learn how to lead authentically and with integrity",
                "learning_objectives": [
                    "Understand principles of authentic leadership",
                    "Learn how to align actions with values",
                    "Develop approaches for leading with integrity in challenging situations",
                    "Create a personal authentic leadership framework"
                ],
                "estimated_time_hours": 15
            },
            {
                "id": "pe_energy",
                "title": "Energy Management and Sustainable Performance",
                "description": "Learn how to manage energy for sustainable high performance",
                "learning_objectives": [
                    "Understand the principles of energy management",
                    "Learn how to optimize physical, emotional, mental, and spiritual energy",
                    "Develop practices for sustainable high performance",
                    "Create a personal energy management plan"
                ],
                "estimated_time_hours": 12
            }
        ],
        SkillLevel.ADVANCED: [
            {
                "id": "pe_purpose",
                "title": "Purpose-Driven Leadership",
                "description": "Learn how to connect leadership to deeper purpose",
                "learning_objectives": [
                    "Understand principles of purpose-driven leadership",
                    "Learn how to identify and articulate personal purpose",
                    "Develop approaches for connecting organizational purpose to personal purpose",
                    "Create a purpose-driven leadership framework"
                ],
                "estimated_time_hours": 18
            },
            {
                "id": "pe_wisdom",
                "title": "Developing Leadership Wisdom",
                "description": "Learn how to develop wisdom and judgment",
                "learning_objectives": [
                    "Understand the nature of wisdom and good judgment",
                    "Learn how to learn from experience and others",
                    "Develop practices for reflection and perspective-taking",
                    "Create a personal wisdom development plan"
                ],
                "estimated_time_hours": 20
            }
        ],
        SkillLevel.EXPERT: [
            {
                "id": "pe_legacy",
                "title": "Creating a Meaningful Legacy",
                "description": "Learn how to create a meaningful and lasting legacy",
                "learning_objectives": [
                    "Understand principles of legacy creation",
                    "Learn how to identify the impact you want to have",
                    "Develop approaches for creating lasting positive change",
                    "Create a legacy plan"
                ],
                "estimated_time_hours": 25
            },
            {
                "id": "pe_mastery",
                "title": "Leadership Mastery and Integration",
                "description": "Learn how to integrate all aspects of leadership into a coherent whole",
                "learning_objectives": [
                    "Understand principles of leadership mastery",
                    "Learn how to integrate strategic, operational, and personal leadership",
                    "Develop practices for continuous evolution and renewal",
                    "Create a personal leadership mastery plan"
                ],
                "estimated_time_hours": 30
            }
        ]
    }
}

class CurriculumEngine:
    """Engine for generating personalized training curricula"""
    
    def __init__(self):
        """Initialize the curriculum engine"""
        self.embedding_engine = get_embedding_engine()
        self.repository = load_repository() if REPO_AVAILABLE else None
        
        # Load resources and scenarios
        self.resources = self._load_resources()
        self.scenarios = self._load_scenarios()
    
    def generate_training_plan(self, trainee_profile: TraineeProfile) -> TrainingPlan:
        """Generate a personalized training plan for a trainee"""
        # Create a new training plan
        training_plan = TrainingPlan(
            trainee_id=trainee_profile.id,
            focus_areas=[],
            role_model_influences=trainee_profile.role_models
        )
        
        # Determine focus areas based on skill levels
        skill_levels = {
            "strategic_philosophy": trainee_profile.strategic_philosophy.level,
            "leadership_style": trainee_profile.leadership_style.level,
            "operational_cadence": trainee_profile.operational_cadence.level,
            "personal_ethos": trainee_profile.personal_ethos.level
        }
        
        # Sort pillars by skill level (ascending) to focus on areas needing most development
        sorted_pillars = sorted(skill_levels.items(), key=lambda x: self._skill_level_to_numeric(x[1]))
        
        # Select the two lowest pillars as focus areas
        focus_pillars = [pillar for pillar, _ in sorted_pillars[:2]]
        training_plan.focus_areas = focus_pillars
        
        # Select modules for each pillar
        modules = []
        
        # First, add modules for focus areas (2 modules each)
        for pillar in focus_pillars:
            level = skill_levels[pillar]
            pillar_modules = self._select_modules_for_pillar(pillar, level, 2)
            modules.extend(pillar_modules)
        
        # Then, add modules for other pillars (1 module each)
        for pillar, level in skill_levels.items():
            if pillar not in focus_pillars:
                pillar_modules = self._select_modules_for_pillar(pillar, level, 1)
                modules.extend(pillar_modules)
        
        # Add module IDs to training plan
        training_plan.modules = [module.id for module in modules]
        
        # Calculate total modules and completion percentage
        training_plan.completion_percentage = 0.0  # Starting point
        
        return training_plan
    
    def get_module_details(self, module_id: str) -> Optional[TrainingModule]:
        """Get details for a specific module"""
        # Check all pillars and levels for the module
        for pillar, levels in BASE_MODULES.items():
            for level, modules in levels.items():
                for module_data in modules:
                    if module_data["id"] == module_id:
                        # Found the module, create a TrainingModule object
                        module = TrainingModule(
                            id=module_data["id"],
                            title=module_data["title"],
                            description=module_data["description"],
                            pillar=pillar,
                            skill_level=level,
                            learning_objectives=module_data["learning_objectives"],
                            estimated_time_hours=module_data["estimated_time_hours"],
                            resources=[],
                            scenarios=[]
                        )
                        
                        # Add relevant resources
                        module.resources = self._select_resources_for_module(module)
                        
                        # Add relevant scenarios
                        module.scenarios = self._select_scenarios_for_module(module)
                        
                        return module
        
        return None
    
    def get_next_module(self, training_plan: TrainingPlan) -> Optional[TrainingModule]:
        """Get the next module in the training plan"""
        if training_plan.current_module_index >= len(training_plan.modules):
            return None
        
        module_id = training_plan.modules[training_plan.current_module_index]
        return self.get_module_details(module_id)
    
    def mark_module_completed(self, training_plan: TrainingPlan) -> TrainingPlan:
        """Mark the current module as completed and update the training plan"""
        if training_plan.current_module_index < len(training_plan.modules):
            # Increment current module index
            training_plan.current_module_index += 1
            
            # Update completion percentage
            training_plan.completion_percentage = (training_plan.current_module_index / len(training_plan.modules)) * 100
        
        return training_plan
    
    def _select_modules_for_pillar(self, pillar: str, level: SkillLevel, count: int) -> List[TrainingModule]:
        """Select modules for a pillar and skill level"""
        modules = []
        
        # Get modules for the pillar and level
        if pillar in BASE_MODULES and level in BASE_MODULES[pillar]:
            pillar_modules = BASE_MODULES[pillar][level]
            
            # Select random modules if there are more than requested
            if len(pillar_modules) > count:
                selected_modules = random.sample(pillar_modules, count)
            else:
                selected_modules = pillar_modules
            
            # Convert to TrainingModule objects
            for module_data in selected_modules:
                module = TrainingModule(
                    id=module_data["id"],
                    title=module_data["title"],
                    description=module_data["description"],
                    pillar=pillar,
                    skill_level=level,
                    learning_objectives=module_data["learning_objectives"],
                    estimated_time_hours=module_data["estimated_time_hours"],
                    resources=[],
                    scenarios=[]
                )
                modules.append(module)
        
        return modules
    
    def _select_resources_for_module(self, module: TrainingModule) -> List[str]:
        """Select relevant resources for a module"""
        # In a real implementation, this would query a database of resources
        # For now, return placeholder resource IDs
        return [f"resource_{module.id}_{i}" for i in range(3)]
    
    def _select_scenarios_for_module(self, module: TrainingModule) -> List[str]:
        """Select relevant scenarios for a module"""
        # In a real implementation, this would query a database of scenarios
        # For now, return placeholder scenario IDs
        return [f"scenario_{module.id}_{i}" for i in range(2)]
    
    def _load_resources(self) -> Dict[str, LearningResource]:
        """Load learning resources"""
        # In a real implementation, this would load from a database
        # For now, return an empty dictionary
        return {}
    
    def _load_scenarios(self) -> Dict[str, TrainingScenario]:
        """Load training scenarios"""
        # In a real implementation, this would load from a database
        # For now, return an empty dictionary
        return {}
    
    def _skill_level_to_numeric(self, level: SkillLevel) -> int:
        """Convert skill level to numeric value"""
        mapping = {
            SkillLevel.NOVICE: 1,
            SkillLevel.DEVELOPING: 2,
            SkillLevel.PROFICIENT: 3,
            SkillLevel.ADVANCED: 4,
            SkillLevel.EXPERT: 5
        }
        return mapping.get(level, 1)
