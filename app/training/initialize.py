#!/usr/bin/env python3
"""
Initialize the CEO training program with a sample trainee.
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.training.main import CEOTrainingProgram
from app.training.models import SkillLevel

def initialize_sample_trainee():
    """Initialize the CEO training program with a sample trainee"""
    logger.info("Initializing CEO training program with sample trainee...")
    
    # Create program
    program = CEOTrainingProgram()
    
    # Create trainee
    trainee = program.create_trainee(
        name="Sample User",
        current_role="Director of Operations",
        target_role="CEO",
        industry="Technology",
        years_experience=10
    )
    
    logger.info(f"Created trainee: {trainee.id}")
    
    # Sample assessment answers
    answers = {
        # Strategic Philosophy questions
        "sp_vision": "I can articulate a clear vision and connect it to current initiatives",
        "sp_innovation": "I regularly seek out and evaluate new ideas for potential implementation",
        "sp_competition": "I regularly analyze competitors and adjust our strategy accordingly",
        "sp_risk": "I balance risk and reward across our strategic initiatives",
        
        # Leadership Style questions
        "ls_hiring": "I hire for both skills and cultural fit with clear criteria",
        "ls_culture": "I articulate values and reinforce them through recognition and feedback",
        "ls_communication": "I communicate consistently across multiple channels with clear messages",
        "ls_development": "I create development plans and provide regular coaching",
        
        # Operational Cadence questions
        "oc_meetings": "I run efficient meetings with agendas and action items",
        "oc_decisions": "I use a consistent process with relevant data and stakeholder input",
        "oc_metrics": "I use a balanced set of metrics to monitor performance",
        "oc_execution": "I have a tracking system for commitments and regular reviews",
        
        # Personal Ethos questions
        "pe_principles": "I consistently apply my values to major decisions",
        "pe_learning": "I have a regular learning practice across multiple domains",
        "pe_resilience": "I learn from failures and use them to improve",
        "pe_balance": "I have boundaries and practices that help maintain balance"
    }
    
    # Process assessment
    updated_trainee = program.process_assessment(trainee.id, answers)
    
    logger.info("Processed assessment")
    logger.info(f"Strategic Philosophy: {updated_trainee.strategic_philosophy.level}")
    logger.info(f"Leadership Style: {updated_trainee.leadership_style.level}")
    logger.info(f"Operational Cadence: {updated_trainee.operational_cadence.level}")
    logger.info(f"Personal Ethos: {updated_trainee.personal_ethos.level}")
    
    # Identify role models
    role_models = program.identify_role_models(trainee.id)
    
    if role_models:
        logger.info("Identified role models:")
        for model in role_models:
            logger.info(f"- {model['name']} ({model['similarity']:.2f})")
    
    # Create training plan
    training_plan = program.create_training_plan(trainee.id)
    
    logger.info("Created training plan")
    logger.info(f"Focus Areas: {', '.join(training_plan.focus_areas)}")
    logger.info(f"Total Modules: {len(training_plan.modules)}")
    
    # Get current module
    module = program.get_current_module(trainee.id)
    
    if module:
        logger.info(f"First module: {module.title}")
    
    logger.info("Sample trainee initialization complete")
    logger.info(f"To explore the training program, use: python -m app.training.cli show {trainee.id}")

if __name__ == "__main__":
    initialize_sample_trainee()
