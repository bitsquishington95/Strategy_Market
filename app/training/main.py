"""
Main module for the CEO training program.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import sys
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.training.models import (
    TraineeProfile, TrainingModule, LearningResource, 
    TrainingScenario, TrainingPlan, ScenarioSubmission,
    ProgressReport, SkillLevel
)
from app.training.assessment import AssessmentEngine
from app.training.curriculum import CurriculumEngine
from app.training.scenarios import ScenariosEngine

class CEOTrainingProgram:
    """Main class for the CEO training program"""
    
    def __init__(self):
        """Initialize the CEO training program"""
        self.assessment_engine = AssessmentEngine()
        self.curriculum_engine = CurriculumEngine()
        self.scenarios_engine = ScenariosEngine()
        
        # Storage for trainees, plans, and submissions
        self.trainees = {}
        self.training_plans = {}
        self.scenario_submissions = {}
        
        # Load data if available
        self._load_data()
    
    def create_trainee(self, name: str, current_role: str, target_role: str, 
                      industry: Optional[str] = None, years_experience: int = 0) -> TraineeProfile:
        """Create a new trainee profile"""
        trainee = self.assessment_engine.create_initial_profile(
            name=name,
            current_role=current_role,
            target_role=target_role,
            industry=industry,
            years_experience=years_experience
        )
        
        # Store trainee
        self.trainees[trainee.id] = trainee
        self._save_data()
        
        return trainee
    
    def process_assessment(self, trainee_id: str, answers: Dict[str, str]) -> TraineeProfile:
        """Process assessment answers and update trainee profile"""
        if trainee_id not in self.trainees:
            logger.warning(f"Trainee not found: {trainee_id}")
            return None
        
        trainee = self.trainees[trainee_id]
        
        # Process assessment
        updated_trainee = self.assessment_engine.process_assessment_answers(trainee, answers)
        
        # Update trainee
        self.trainees[trainee_id] = updated_trainee
        self._save_data()
        
        return updated_trainee
    
    def identify_role_models(self, trainee_id: str, top_n: int = 3) -> List[Dict[str, Any]]:
        """Identify CEO role models for a trainee"""
        if trainee_id not in self.trainees:
            logger.warning(f"Trainee not found: {trainee_id}")
            return []
        
        trainee = self.trainees[trainee_id]
        
        # Identify role models
        role_models = self.assessment_engine.identify_role_models(trainee, top_n)
        
        # Update trainee with role models
        trainee.role_models = [rm["name"] for rm in role_models]
        self.trainees[trainee_id] = trainee
        self._save_data()
        
        return role_models
    
    def generate_growth_recommendations(self, trainee_id: str) -> Dict[str, List[str]]:
        """Generate growth recommendations for a trainee"""
        if trainee_id not in self.trainees:
            logger.warning(f"Trainee not found: {trainee_id}")
            return {}
        
        trainee = self.trainees[trainee_id]
        
        # Generate recommendations
        return self.assessment_engine.generate_growth_recommendations(trainee)
    
    def create_training_plan(self, trainee_id: str) -> TrainingPlan:
        """Create a personalized training plan for a trainee"""
        if trainee_id not in self.trainees:
            logger.warning(f"Trainee not found: {trainee_id}")
            return None
        
        trainee = self.trainees[trainee_id]
        
        # Generate training plan
        training_plan = self.curriculum_engine.generate_training_plan(trainee)
        
        # Store training plan
        self.training_plans[trainee_id] = training_plan
        self._save_data()
        
        return training_plan
    
    def get_current_module(self, trainee_id: str) -> Optional[TrainingModule]:
        """Get the current module for a trainee"""
        if trainee_id not in self.training_plans:
            logger.warning(f"Training plan not found for trainee: {trainee_id}")
            return None
        
        training_plan = self.training_plans[trainee_id]
        
        # Get current module
        return self.curriculum_engine.get_next_module(training_plan)
    
    def complete_current_module(self, trainee_id: str) -> TrainingPlan:
        """Mark the current module as completed for a trainee"""
        if trainee_id not in self.training_plans:
            logger.warning(f"Training plan not found for trainee: {trainee_id}")
            return None
        
        if trainee_id not in self.trainees:
            logger.warning(f"Trainee not found: {trainee_id}")
            return None
        
        training_plan = self.training_plans[trainee_id]
        trainee = self.trainees[trainee_id]
        
        # Get current module
        current_module = self.curriculum_engine.get_next_module(training_plan)
        if current_module:
            # Add to completed modules
            if current_module.id not in trainee.completed_modules:
                trainee.completed_modules.append(current_module.id)
                self.trainees[trainee_id] = trainee
            
            # Mark as completed
            updated_plan = self.curriculum_engine.mark_module_completed(training_plan)
            self.training_plans[trainee_id] = updated_plan
            self._save_data()
            
            return updated_plan
        
        return training_plan
    
    def get_scenario(self, scenario_id: str) -> Optional[TrainingScenario]:
        """Get a specific scenario"""
        return self.scenarios_engine.get_scenario(scenario_id)
    
    def get_scenarios_for_module(self, module_id: str) -> List[TrainingScenario]:
        """Get scenarios for a specific module"""
        # Get module details
        module = self.curriculum_engine.get_module_details(module_id)
        if not module:
            logger.warning(f"Module not found: {module_id}")
            return []
        
        # Get scenarios
        scenarios = []
        for scenario_id in module.scenarios:
            scenario = self.scenarios_engine.get_scenario(scenario_id)
            if scenario:
                scenarios.append(scenario)
        
        return scenarios
    
    def submit_scenario_response(self, trainee_id: str, scenario_id: str, 
                               approach: str, principles_applied: List[str]) -> ScenarioSubmission:
        """Submit a response to a scenario"""
        if trainee_id not in self.trainees:
            logger.warning(f"Trainee not found: {trainee_id}")
            return None
        
        # Create submission
        submission_id = f"{trainee_id}_{scenario_id}_{uuid.uuid4().hex[:8]}"
        submission = ScenarioSubmission(
            trainee_id=trainee_id,
            scenario_id=scenario_id,
            approach=approach,
            principles_applied=principles_applied
        )
        
        # Evaluate submission
        evaluated_submission = self.scenarios_engine.evaluate_submission(submission)
        
        # Store submission
        self.scenario_submissions[submission_id] = evaluated_submission
        
        # Update trainee's completed scenarios
        trainee = self.trainees[trainee_id]
        if scenario_id not in trainee.completed_scenarios:
            trainee.completed_scenarios.append(scenario_id)
            self.trainees[trainee_id] = trainee
        
        self._save_data()
        
        return evaluated_submission
    
    def generate_progress_report(self, trainee_id: str) -> ProgressReport:
        """Generate a progress report for a trainee"""
        if trainee_id not in self.trainees:
            logger.warning(f"Trainee not found: {trainee_id}")
            return None
        
        trainee = self.trainees[trainee_id]
        
        # Create progress report
        report = ProgressReport(
            trainee_id=trainee_id,
            report_date=datetime.now()
        )
        
        # Set modules completed
        report.modules_completed = len(trainee.completed_modules)
        
        # Set scenarios completed
        report.scenarios_completed = len(trainee.completed_scenarios)
        
        # Set total modules
        if trainee_id in self.training_plans:
            training_plan = self.training_plans[trainee_id]
            report.total_modules = len(training_plan.modules)
        
        # Set total scenarios (approximate based on modules)
        report.total_scenarios = report.total_modules * 2  # Assuming 2 scenarios per module
        
        # Set skill levels
        report.skill_levels = {
            "strategic_philosophy": trainee.strategic_philosophy.level,
            "leadership_style": trainee.leadership_style.level,
            "operational_cadence": trainee.operational_cadence.level,
            "personal_ethos": trainee.personal_ethos.level
        }
        
        # Set strengths and focus areas
        for pillar, level in report.skill_levels.items():
            if self._skill_level_to_numeric(level) >= 4:  # Advanced or Expert
                report.strengths.append(pillar)
            elif self._skill_level_to_numeric(level) <= 2:  # Novice or Developing
                report.focus_areas.append(pillar)
        
        # Set CEO archetype and similarities
        # This would require additional analysis in a real implementation
        report.archetype = "Emerging Leader"  # Placeholder
        
        # Get similar CEOs from submissions
        ceo_similarities = {}
        for submission_id, submission in self.scenario_submissions.items():
            if submission.trainee_id == trainee_id:
                for ceo_sim in submission.similar_ceos:
                    ceo_name = ceo_sim["ceo"]
                    similarity = ceo_sim["similarity"]
                    
                    if ceo_name in ceo_similarities:
                        ceo_similarities[ceo_name] = (ceo_similarities[ceo_name] + similarity) / 2
                    else:
                        ceo_similarities[ceo_name] = similarity
        
        # Convert to list and sort
        similar_ceos = [{"ceo_name": name, "similarity": score} for name, score in ceo_similarities.items()]
        similar_ceos.sort(key=lambda x: x["similarity"], reverse=True)
        
        report.similar_ceos = similar_ceos[:3]  # Top 3
        
        return report
    
    def _load_data(self):
        """Load data from files"""
        data_dir = Path(__file__).parent.parent.parent / "data" / "training"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load trainees
        trainees_file = data_dir / "trainees.json"
        if trainees_file.exists():
            try:
                with open(trainees_file, "r") as f:
                    trainees_data = json.load(f)
                
                for trainee_id, trainee_data in trainees_data.items():
                    self.trainees[trainee_id] = TraineeProfile(**trainee_data)
            except Exception as e:
                logger.error(f"Error loading trainees: {e}")
        
        # Load training plans
        plans_file = data_dir / "training_plans.json"
        if plans_file.exists():
            try:
                with open(plans_file, "r") as f:
                    plans_data = json.load(f)
                
                for trainee_id, plan_data in plans_data.items():
                    self.training_plans[trainee_id] = TrainingPlan(**plan_data)
            except Exception as e:
                logger.error(f"Error loading training plans: {e}")
        
        # Load scenario submissions
        submissions_file = data_dir / "scenario_submissions.json"
        if submissions_file.exists():
            try:
                with open(submissions_file, "r") as f:
                    submissions_data = json.load(f)
                
                for submission_id, submission_data in submissions_data.items():
                    self.scenario_submissions[submission_id] = ScenarioSubmission(**submission_data)
            except Exception as e:
                logger.error(f"Error loading scenario submissions: {e}")
    
    def _save_data(self):
        """Save data to files"""
        data_dir = Path(__file__).parent.parent.parent / "data" / "training"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save trainees
        trainees_file = data_dir / "trainees.json"
        try:
            with open(trainees_file, "w") as f:
                trainees_data = {trainee_id: trainee.dict() for trainee_id, trainee in self.trainees.items()}
                json.dump(trainees_data, f, default=self._json_serializer, indent=2)
        except Exception as e:
            logger.error(f"Error saving trainees: {e}")
        
        # Save training plans
        plans_file = data_dir / "training_plans.json"
        try:
            with open(plans_file, "w") as f:
                plans_data = {trainee_id: plan.dict() for trainee_id, plan in self.training_plans.items()}
                json.dump(plans_data, f, default=self._json_serializer, indent=2)
        except Exception as e:
            logger.error(f"Error saving training plans: {e}")
        
        # Save scenario submissions
        submissions_file = data_dir / "scenario_submissions.json"
        try:
            with open(submissions_file, "w") as f:
                submissions_data = {sub_id: sub.dict() for sub_id, sub in self.scenario_submissions.items()}
                json.dump(submissions_data, f, default=self._json_serializer, indent=2)
        except Exception as e:
            logger.error(f"Error saving scenario submissions: {e}")
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for objects not serializable by default"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, SkillLevel):
            return obj.value
        raise TypeError(f"Type {type(obj)} not serializable")
    
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
