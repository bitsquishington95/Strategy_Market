#!/usr/bin/env python3
"""
Command-line interface for the CEO training program.
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import textwrap
from tabulate import tabulate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.training.main import CEOTrainingProgram
from app.training.models import SkillLevel

class CEOTrainingCLI:
    """Command-line interface for the CEO training program"""
    
    def __init__(self):
        """Initialize the CLI"""
        self.program = CEOTrainingProgram()
    
    def run(self):
        """Run the CLI"""
        parser = argparse.ArgumentParser(description="CEO Training Program CLI")
        subparsers = parser.add_subparsers(dest="command", help="Command to run")
        
        # Create trainee command
        create_parser = subparsers.add_parser("create", help="Create a new trainee profile")
        create_parser.add_argument("name", help="Trainee name")
        create_parser.add_argument("current_role", help="Current role")
        create_parser.add_argument("target_role", help="Target role")
        create_parser.add_argument("--industry", help="Industry")
        create_parser.add_argument("--years", type=int, default=0, help="Years of experience")
        
        # List trainees command
        subparsers.add_parser("list", help="List all trainees")
        
        # Show trainee command
        show_parser = subparsers.add_parser("show", help="Show trainee details")
        show_parser.add_argument("trainee_id", help="Trainee ID")
        
        # Assessment command
        assess_parser = subparsers.add_parser("assess", help="Take skill assessment")
        assess_parser.add_argument("trainee_id", help="Trainee ID")
        
        # Role models command
        models_parser = subparsers.add_parser("models", help="Identify role models")
        models_parser.add_argument("trainee_id", help="Trainee ID")
        models_parser.add_argument("--top", type=int, default=3, help="Number of role models to identify")
        
        # Recommendations command
        rec_parser = subparsers.add_parser("recommend", help="Get growth recommendations")
        rec_parser.add_argument("trainee_id", help="Trainee ID")
        
        # Create training plan command
        plan_parser = subparsers.add_parser("plan", help="Create training plan")
        plan_parser.add_argument("trainee_id", help="Trainee ID")
        
        # Show current module command
        module_parser = subparsers.add_parser("module", help="Show current module")
        module_parser.add_argument("trainee_id", help="Trainee ID")
        
        # Complete module command
        complete_parser = subparsers.add_parser("complete", help="Complete current module")
        complete_parser.add_argument("trainee_id", help="Trainee ID")
        
        # Show scenario command
        scenario_parser = subparsers.add_parser("scenario", help="Show scenario details")
        scenario_parser.add_argument("scenario_id", help="Scenario ID")
        
        # Submit scenario response command
        submit_parser = subparsers.add_parser("submit", help="Submit scenario response")
        submit_parser.add_argument("trainee_id", help="Trainee ID")
        submit_parser.add_argument("scenario_id", help="Scenario ID")
        submit_parser.add_argument("--approach", help="Approach (or path to file containing approach)")
        submit_parser.add_argument("--principles", help="Comma-separated list of principles applied")
        
        # Progress report command
        progress_parser = subparsers.add_parser("progress", help="Generate progress report")
        progress_parser.add_argument("trainee_id", help="Trainee ID")
        
        # Parse arguments
        args = parser.parse_args()
        
        # Execute command
        if args.command == "create":
            self._create_trainee(args)
        elif args.command == "list":
            self._list_trainees()
        elif args.command == "show":
            self._show_trainee(args)
        elif args.command == "assess":
            self._take_assessment(args)
        elif args.command == "models":
            self._identify_role_models(args)
        elif args.command == "recommend":
            self._show_recommendations(args)
        elif args.command == "plan":
            self._create_training_plan(args)
        elif args.command == "module":
            self._show_current_module(args)
        elif args.command == "complete":
            self._complete_module(args)
        elif args.command == "scenario":
            self._show_scenario(args)
        elif args.command == "submit":
            self._submit_scenario_response(args)
        elif args.command == "progress":
            self._show_progress_report(args)
        else:
            parser.print_help()
    
    def _create_trainee(self, args):
        """Create a new trainee profile"""
        trainee = self.program.create_trainee(
            name=args.name,
            current_role=args.current_role,
            target_role=args.target_role,
            industry=args.industry,
            years_experience=args.years
        )
        
        print(f"\nTrainee created successfully!")
        print(f"ID: {trainee.id}")
        print(f"Name: {trainee.name}")
        print(f"Current Role: {trainee.current_role}")
        print(f"Target Role: {trainee.target_role}")
        if trainee.industry:
            print(f"Industry: {trainee.industry}")
        print(f"Years Experience: {trainee.years_experience}")
        print("\nNext step: Take the skill assessment with:")
        print(f"  python -m app.training.cli assess {trainee.id}")
    
    def _list_trainees(self):
        """List all trainees"""
        if not self.program.trainees:
            print("No trainees found.")
            return
        
        # Prepare table data
        headers = ["ID", "Name", "Current Role", "Target Role", "Industry", "Years"]
        rows = []
        
        for trainee_id, trainee in self.program.trainees.items():
            rows.append([
                trainee_id,
                trainee.name,
                trainee.current_role,
                trainee.target_role,
                trainee.industry or "N/A",
                trainee.years_experience
            ])
        
        # Print table
        print("\nTrainees:")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    def _show_trainee(self, args):
        """Show trainee details"""
        trainee_id = args.trainee_id
        if trainee_id not in self.program.trainees:
            print(f"Trainee not found: {trainee_id}")
            return
        
        trainee = self.program.trainees[trainee_id]
        
        print("\nTrainee Profile:")
        print(f"ID: {trainee.id}")
        print(f"Name: {trainee.name}")
        print(f"Current Role: {trainee.current_role}")
        print(f"Target Role: {trainee.target_role}")
        if trainee.industry:
            print(f"Industry: {trainee.industry}")
        print(f"Years Experience: {trainee.years_experience}")
        
        print("\nSkill Levels:")
        print(f"Strategic Philosophy: {trainee.strategic_philosophy.level.value}")
        print(f"Leadership Style: {trainee.leadership_style.level.value}")
        print(f"Operational Cadence: {trainee.operational_cadence.level.value}")
        print(f"Personal Ethos: {trainee.personal_ethos.level.value}")
        
        if trainee.role_models:
            print("\nRole Models:")
            for model in trainee.role_models:
                print(f"- {model}")
        
        if trainee.completed_modules:
            print("\nCompleted Modules:")
            for module_id in trainee.completed_modules:
                print(f"- {module_id}")
        
        if trainee.completed_scenarios:
            print("\nCompleted Scenarios:")
            for scenario_id in trainee.completed_scenarios:
                print(f"- {scenario_id}")
    
    def _take_assessment(self, args):
        """Take skill assessment"""
        trainee_id = args.trainee_id
        if trainee_id not in self.program.trainees:
            print(f"Trainee not found: {trainee_id}")
            return
        
        print("\nSkill Assessment")
        print("================")
        print("Answer the following questions to assess your current skill levels.")
        print("For each question, enter the number that best matches your current approach.")
        
        answers = {}
        
        # Strategic Philosophy questions
        print("\nStrategic Philosophy")
        print("-------------------")
        for i, question in enumerate(self.program.assessment_engine.ASSESSMENT_QUESTIONS["strategic_philosophy"]):
            self._ask_assessment_question(question, answers)
        
        # Leadership Style questions
        print("\nLeadership Style")
        print("---------------")
        for i, question in enumerate(self.program.assessment_engine.ASSESSMENT_QUESTIONS["leadership_style"]):
            self._ask_assessment_question(question, answers)
        
        # Operational Cadence questions
        print("\nOperational Cadence")
        print("------------------")
        for i, question in enumerate(self.program.assessment_engine.ASSESSMENT_QUESTIONS["operational_cadence"]):
            self._ask_assessment_question(question, answers)
        
        # Personal Ethos questions
        print("\nPersonal Ethos")
        print("-------------")
        for i, question in enumerate(self.program.assessment_engine.ASSESSMENT_QUESTIONS["personal_ethos"]):
            self._ask_assessment_question(question, answers)
        
        # Process assessment
        updated_trainee = self.program.process_assessment(trainee_id, answers)
        
        print("\nAssessment completed!")
        print("\nYour skill levels:")
        print(f"Strategic Philosophy: {updated_trainee.strategic_philosophy.level.value}")
        print(f"Leadership Style: {updated_trainee.leadership_style.level.value}")
        print(f"Operational Cadence: {updated_trainee.operational_cadence.level.value}")
        print(f"Personal Ethos: {updated_trainee.personal_ethos.level.value}")
        
        print("\nNext step: Identify role models with:")
        print(f"  python -m app.training.cli models {trainee_id}")
    
    def _ask_assessment_question(self, question, answers):
        """Ask an assessment question and record the answer"""
        print(f"\n{question['question']}")
        
        # Print options
        for i, (level, description) in enumerate(question["skill_mapping"].items(), 1):
            print(f"{i}. {description}")
        
        # Get answer
        while True:
            try:
                choice = int(input("\nYour answer (1-5): "))
                if 1 <= choice <= 5:
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Map choice to skill level
        levels = list(question["skill_mapping"].keys())
        selected_level = levels[choice - 1]
        selected_description = question["skill_mapping"][selected_level]
        
        # Record answer
        answers[question["id"]] = selected_description
    
    def _identify_role_models(self, args):
        """Identify role models"""
        trainee_id = args.trainee_id
        if trainee_id not in self.program.trainees:
            print(f"Trainee not found: {trainee_id}")
            return
        
        print("\nIdentifying role models...")
        role_models = self.program.identify_role_models(trainee_id, args.top)
        
        if not role_models:
            print("No role models identified. This may be due to the repository not being available.")
            return
        
        print("\nYour CEO role models:")
        for i, model in enumerate(role_models, 1):
            print(f"\n{i}. {model['name']}")
            if model.get("company"):
                print(f"   Company: {model['company']}")
            if model.get("industry"):
                print(f"   Industry: {model['industry']}")
            print(f"   Similarity: {model['similarity']:.2f}")
        
        print("\nNext step: Get growth recommendations with:")
        print(f"  python -m app.training.cli recommend {trainee_id}")
    
    def _show_recommendations(self, args):
        """Show growth recommendations"""
        trainee_id = args.trainee_id
        if trainee_id not in self.program.trainees:
            print(f"Trainee not found: {trainee_id}")
            return
        
        recommendations = self.program.generate_growth_recommendations(trainee_id)
        
        print("\nGrowth Recommendations")
        print("=====================")
        
        for pillar, recs in recommendations.items():
            print(f"\n{pillar.replace('_', ' ').title()}:")
            for rec in recs:
                print(f"- {rec}")
        
        print("\nNext step: Create your training plan with:")
        print(f"  python -m app.training.cli plan {trainee_id}")
    
    def _create_training_plan(self, args):
        """Create a training plan"""
        trainee_id = args.trainee_id
        if trainee_id not in self.program.trainees:
            print(f"Trainee not found: {trainee_id}")
            return
        
        print("\nCreating personalized training plan...")
        training_plan = self.program.create_training_plan(trainee_id)
        
        print("\nTraining Plan Created!")
        print(f"Focus Areas: {', '.join(training_plan.focus_areas)}")
        print(f"Total Modules: {len(training_plan.modules)}")
        print(f"Completion: {training_plan.completion_percentage:.1f}%")
        
        print("\nNext step: Start your first module with:")
        print(f"  python -m app.training.cli module {trainee_id}")
    
    def _show_current_module(self, args):
        """Show current module"""
        trainee_id = args.trainee_id
        if trainee_id not in self.program.trainees:
            print(f"Trainee not found: {trainee_id}")
            return
        
        if trainee_id not in self.program.training_plans:
            print(f"No training plan found for trainee: {trainee_id}")
            print(f"Create a training plan first with: python -m app.training.cli plan {trainee_id}")
            return
        
        module = self.program.get_current_module(trainee_id)
        if not module:
            print("No more modules in your training plan. Congratulations on completing the program!")
            return
        
        print(f"\nModule: {module.title}")
        print("=" * (len(module.title) + 8))
        print(f"ID: {module.id}")
        print(f"Pillar: {module.pillar}")
        print(f"Skill Level: {module.skill_level.value}")
        print(f"Estimated Time: {module.estimated_time_hours} hours")
        
        print("\nDescription:")
        print(textwrap.fill(module.description, width=80))
        
        print("\nLearning Objectives:")
        for i, objective in enumerate(module.learning_objectives, 1):
            print(f"{i}. {objective}")
        
        if module.resources:
            print("\nResources:")
            for resource_id in module.resources:
                print(f"- {resource_id}")
        
        if module.scenarios:
            print("\nScenarios:")
            for scenario_id in module.scenarios:
                print(f"- {scenario_id}")
                # Get scenario details if available
                scenario = self.program.get_scenario(scenario_id)
                if scenario:
                    print(f"  {scenario.title}")
        
        print("\nTo complete this module:")
        print(f"  python -m app.training.cli complete {trainee_id}")
        
        if module.scenarios:
            print("\nTo work on a scenario:")
            print(f"  python -m app.training.cli scenario {module.scenarios[0]}")
    
    def _complete_module(self, args):
        """Complete current module"""
        trainee_id = args.trainee_id
        if trainee_id not in self.program.trainees:
            print(f"Trainee not found: {trainee_id}")
            return
        
        if trainee_id not in self.program.training_plans:
            print(f"No training plan found for trainee: {trainee_id}")
            return
        
        # Get current module before completing it
        current_module = self.program.get_current_module(trainee_id)
        if not current_module:
            print("No more modules in your training plan.")
            return
        
        # Complete module
        updated_plan = self.program.complete_current_module(trainee_id)
        
        print(f"\nModule '{current_module.title}' completed!")
        print(f"Progress: {updated_plan.completion_percentage:.1f}% ({updated_plan.current_module_index}/{len(updated_plan.modules)} modules)")
        
        # Check if there's another module
        next_module = self.program.get_current_module(trainee_id)
        if next_module:
            print("\nNext module:")
            print(f"  {next_module.title}")
            print("\nTo start the next module:")
            print(f"  python -m app.training.cli module {trainee_id}")
        else:
            print("\nCongratulations! You have completed all modules in your training plan.")
            print("\nTo see your progress report:")
            print(f"  python -m app.training.cli progress {trainee_id}")
    
    def _show_scenario(self, args):
        """Show scenario details"""
        scenario_id = args.scenario_id
        scenario = self.program.get_scenario(scenario_id)
        
        if not scenario:
            print(f"Scenario not found: {scenario_id}")
            return
        
        print(f"\nScenario: {scenario.title}")
        print("=" * (len(scenario.title) + 10))
        print(f"ID: {scenario.id}")
        print(f"Pillar: {scenario.pillar}")
        print(f"Difficulty: {scenario.difficulty.value}")
        
        print("\nSituation:")
        print(textwrap.fill(scenario.situation, width=80))
        
        print("\nContext:")
        print(textwrap.fill(scenario.context, width=80))
        
        print("\nCEO Approaches:")
        for ceo, approach in scenario.ceo_approaches.items():
            print(f"\n{ceo}:")
            print(textwrap.fill(approach, width=80, initial_indent="  ", subsequent_indent="  "))
        
        print("\nPrinciples:")
        for principle in scenario.principles:
            print(f"- {principle}")
        
        print("\nEvaluation Criteria:")
        for criterion in scenario.evaluation_criteria:
            print(f"- {criterion}")
        
        print("\nTo submit your response:")
        print(f"  python -m app.training.cli submit [trainee_id] {scenario_id} --approach [your_approach] --principles [principles]")
    
    def _submit_scenario_response(self, args):
        """Submit scenario response"""
        trainee_id = args.trainee_id
        scenario_id = args.scenario_id
        
        if trainee_id not in self.program.trainees:
            print(f"Trainee not found: {trainee_id}")
            return
        
        scenario = self.program.get_scenario(scenario_id)
        if not scenario:
            print(f"Scenario not found: {scenario_id}")
            return
        
        # Get approach
        approach = args.approach
        if not approach:
            print("Please provide your approach with --approach.")
            return
        
        # Check if approach is a file path
        approach_path = Path(approach)
        if approach_path.exists() and approach_path.is_file():
            try:
                with open(approach_path, "r") as f:
                    approach = f.read()
            except Exception as e:
                print(f"Error reading approach file: {e}")
                return
        
        # Get principles
        principles = []
        if args.principles:
            principles = [p.strip() for p in args.principles.split(",")]
        
        # Submit response
        submission = self.program.submit_scenario_response(
            trainee_id=trainee_id,
            scenario_id=scenario_id,
            approach=approach,
            principles_applied=principles
        )
        
        print("\nResponse submitted successfully!")
        
        print("\nFeedback:")
        if submission.feedback:
            print(textwrap.fill(submission.feedback, width=80))
        
        if submission.strengths:
            print("\nStrengths:")
            for strength in submission.strengths:
                print(f"- {strength}")
        
        if submission.improvement_areas:
            print("\nAreas for Improvement:")
            for area in submission.improvement_areas:
                print(f"- {area}")
        
        if submission.similar_ceos:
            print("\nYour approach is similar to:")
            for i, ceo_sim in enumerate(submission.similar_ceos[:3], 1):
                print(f"{i}. {ceo_sim['ceo']} ({ceo_sim['similarity']:.2f})")
    
    def _show_progress_report(self, args):
        """Show progress report"""
        trainee_id = args.trainee_id
        if trainee_id not in self.program.trainees:
            print(f"Trainee not found: {trainee_id}")
            return
        
        report = self.program.generate_progress_report(trainee_id)
        
        print("\nProgress Report")
        print("==============")
        
        print(f"\nModules Completed: {report.modules_completed}/{report.total_modules}")
        print(f"Scenarios Completed: {report.scenarios_completed}/{report.total_scenarios}")
        
        print("\nSkill Levels:")
        for pillar, level in report.skill_levels.items():
            print(f"{pillar.replace('_', ' ').title()}: {level.value}")
        
        if report.strengths:
            print("\nStrengths:")
            for strength in report.strengths:
                print(f"- {strength}")
        
        if report.focus_areas:
            print("\nFocus Areas:")
            for area in report.focus_areas:
                print(f"- {area}")
        
        if report.archetype:
            print(f"\nLeadership Archetype: {report.archetype}")
        
        if report.similar_ceos:
            print("\nSimilar Leadership Styles:")
            for i, ceo_sim in enumerate(report.similar_ceos, 1):
                print(f"{i}. {ceo_sim['ceo_name']} ({ceo_sim['similarity']:.2f})")


if __name__ == "__main__":
    cli = CEOTrainingCLI()
    cli.run()
