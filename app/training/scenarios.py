"""
Training scenarios module for the CEO training program.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.training.models import TrainingScenario, ScenarioSubmission, SkillLevel, TraineeProfile
from app.engine.embeddings import get_embedding_engine

# Try to import repository
try:
    from app.repository.store import Repository, load_repository
    REPO_AVAILABLE = True
except ImportError:
    logger.warning("Repository module not available")
    REPO_AVAILABLE = False

# Sample training scenarios
SAMPLE_SCENARIOS = [
    {
        "id": "scenario_competitive_attack",
        "title": "Responding to Competitive Attack",
        "situation": "A major competitor has just launched a product that directly competes with your flagship offering, at a 30% lower price point with comparable features.",
        "context": "Your company has been the market leader for the past five years. The competitor's move threatens to erode your market share significantly. Your team is looking to you for direction on how to respond.",
        "pillar": "strategic_philosophy",
        "difficulty": SkillLevel.PROFICIENT,
        "ceo_approaches": {
            "Steve Jobs": "Focus on product differentiation and premium experience. Emphasize the unique ecosystem benefits and quality advantages. Don't engage in price war.",
            "Jeff Bezos": "Analyze customer needs deeply. If the competitor is truly delivering equal value at lower cost, find operational efficiencies to match price while maintaining margins. If not, highlight the superior customer experience.",
            "Satya Nadella": "Reframe the competition around broader platform value rather than single product features. Accelerate integration with other offerings to create ecosystem advantages."
        },
        "principles": ["principle:differentiation", "principle:customer_obsession", "principle:ecosystem_thinking"],
        "evaluation_criteria": [
            "Strategic clarity of response",
            "Balance of short-term tactics and long-term positioning",
            "Understanding of competitive dynamics",
            "Alignment with company strengths and values"
        ]
    },
    {
        "id": "scenario_talent_exodus",
        "title": "Addressing a Talent Exodus",
        "situation": "Three senior leaders and several high-performing team members have resigned in the past month, citing better opportunities elsewhere.",
        "context": "Your company has been going through significant changes, including a reorganization and shift in strategic direction. Morale has been declining, and exit interviews suggest concerns about future growth opportunities and work culture.",
        "pillar": "leadership_style",
        "difficulty": SkillLevel.ADVANCED,
        "ceo_approaches": {
            "Satya Nadella": "Conduct listening sessions to understand root causes. Reinforce growth mindset culture and create visible career paths. Personally engage with key talent to share vision and opportunities.",
            "Marc Benioff": "Reaffirm company values and purpose. Create task force of respected leaders to address cultural issues. Implement transparent career development programs tied to new strategic direction.",
            "Indra Nooyi": "Personally reach out to remaining key talent. Conduct thorough analysis of compensation and growth opportunities relative to market. Address work-life balance issues while reinforcing purpose and mission."
        },
        "principles": ["principle:talent_focus", "principle:culture_first", "principle:transparent_communication"],
        "evaluation_criteria": [
            "Depth of root cause analysis",
            "Balance of immediate retention actions and long-term cultural solutions",
            "Personal leadership and visibility",
            "Concrete actions to rebuild trust and engagement"
        ]
    },
    {
        "id": "scenario_missed_targets",
        "title": "Responding to Missed Financial Targets",
        "situation": "Your company has missed quarterly financial targets for the second consecutive quarter, with revenue 15% below projections and increasing cash burn.",
        "context": "The board and investors are concerned about the trajectory. The executive team is divided on whether to cut costs aggressively or maintain investment in growth initiatives. The company has 18 months of runway at current burn rate.",
        "pillar": "operational_cadence",
        "difficulty": SkillLevel.ADVANCED,
        "ceo_approaches": {
            "Jeff Bezos": "Focus on cash flow, not just growth or profits. Conduct detailed operational review to identify inefficiencies. Maintain investment in high-conviction growth areas while cutting elsewhere. Communicate long-term focus to investors.",
            "Jamie Dimon": "Implement immediate cost controls and conduct weekly operational reviews. Create detailed metrics dashboard tracking leading indicators. Hold leaders accountable for specific improvement targets.",
            "Jack Welch": "Set aggressive performance targets. Identify bottom 10% of initiatives by ROI and eliminate. Increase cadence of performance reviews and create war room for financial turnaround."
        },
        "principles": ["principle:operational_discipline", "principle:data_driven", "principle:accountability"],
        "evaluation_criteria": [
            "Balance of short-term stabilization and long-term positioning",
            "Specificity of operational improvements",
            "Quality of measurement and accountability system",
            "Effectiveness of stakeholder communication"
        ]
    },
    {
        "id": "scenario_ethical_dilemma",
        "title": "Navigating an Ethical Dilemma",
        "situation": "Your team has discovered that a new product feature, already announced and scheduled to launch next month, has potential privacy implications that weren't previously understood.",
        "context": "Delaying the launch would impact quarterly results and disappoint customers. Proceeding risks potential regulatory issues and reputational damage if the privacy concerns become public. The technical team believes they can address the issues within 3-4 months.",
        "pillar": "personal_ethos",
        "difficulty": SkillLevel.EXPERT,
        "ceo_approaches": {
            "Satya Nadella": "Delay the launch despite financial impact. Be transparent with customers and shareholders about the reasons. Establish new privacy review protocols to prevent future issues.",
            "Tim Cook": "Take the financial hit and delay the launch. Frame the decision around core values of customer privacy and trust. Use the incident to reinforce privacy as a competitive advantage.",
            "Yvon Chouinard": "Delay launch and be fully transparent about the issues discovered. Use this as an opportunity to raise industry standards around privacy and ethical product development."
        },
        "principles": ["principle:integrity", "principle:long_term_focus", "principle:transparency"],
        "evaluation_criteria": [
            "Clarity of ethical reasoning",
            "Balance of stakeholder interests",
            "Courage to make difficult trade-offs",
            "Learning and process improvement"
        ]
    },
    {
        "id": "scenario_innovation_culture",
        "title": "Building an Innovation Culture",
        "situation": "Your company has been successful with its core products but has struggled to develop breakthrough innovations. The last three new product initiatives have failed to gain market traction.",
        "context": "The industry is evolving rapidly with new technologies and business models. Your company has talented people but is known for a risk-averse culture and slow decision-making processes.",
        "pillar": "strategic_philosophy",
        "difficulty": SkillLevel.ADVANCED,
        "ceo_approaches": {
            "Steve Jobs": "Focus innovation around a few high-impact initiatives with small, elite teams. Create separate innovation unit with different processes and metrics. Personally review and champion promising projects.",
            "Jeff Bezos": "Implement mechanisms like 'working backwards' and six-page memos. Create separate innovation funding pool with different ROI expectations. Celebrate and learn from failures.",
            "Reed Hastings": "Increase talent density and reduce controls. Create high autonomy, high accountability culture. Implement 'innovation days' where teams can work on new ideas."
        },
        "principles": ["principle:innovation_focus", "principle:failure_tolerance", "principle:small_teams"],
        "evaluation_criteria": [
            "Balance of cultural and process changes",
            "Specificity of innovation mechanisms",
            "Approach to risk management and failure",
            "Leadership modeling of desired behaviors"
        ]
    }
]

class ScenariosEngine:
    """Engine for managing training scenarios and evaluating submissions"""
    
    def __init__(self):
        """Initialize the scenarios engine"""
        self.embedding_engine = get_embedding_engine()
        self.repository = load_repository() if REPO_AVAILABLE else None
        
        # Load scenarios
        self.scenarios = self._load_scenarios()
    
    def get_scenario(self, scenario_id: str) -> Optional[TrainingScenario]:
        """Get a specific scenario by ID"""
        return self.scenarios.get(scenario_id)
    
    def get_scenarios_by_pillar(self, pillar: str, difficulty: Optional[SkillLevel] = None) -> List[TrainingScenario]:
        """Get scenarios for a specific pillar and optional difficulty level"""
        results = []
        
        for scenario in self.scenarios.values():
            if scenario.pillar == pillar:
                if difficulty is None or scenario.difficulty == difficulty:
                    results.append(scenario)
        
        return results
    
    def evaluate_submission(self, submission: ScenarioSubmission) -> ScenarioSubmission:
        """Evaluate a scenario submission and provide feedback"""
        # Get the scenario
        scenario = self.get_scenario(submission.scenario_id)
        if not scenario:
            logger.warning(f"Scenario not found: {submission.scenario_id}")
            return submission
        
        # Analyze submission using embeddings
        submission_embedding = self.embedding_engine.embed_text(submission.approach)
        
        # Compare with CEO approaches
        ceo_similarities = []
        for ceo_name, approach in scenario.ceo_approaches.items():
            approach_embedding = self.embedding_engine.embed_text(approach)
            similarity = self.embedding_engine.compute_similarity(submission_embedding, approach_embedding)
            
            ceo_similarities.append({
                "ceo": ceo_name,
                "similarity": similarity
            })
        
        # Sort by similarity (descending)
        ceo_similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Set similar CEOs in submission
        submission.similar_ceos = ceo_similarities
        
        # Analyze principles applied
        principles_applied = submission.principles_applied
        principles_overlap = set(principles_applied).intersection(set(scenario.principles))
        principles_missing = set(scenario.principles) - set(principles_applied)
        
        # Generate feedback
        strengths = []
        improvement_areas = []
        
        # Add strengths based on CEO similarities
        if ceo_similarities and ceo_similarities[0]["similarity"] > 0.7:
            top_ceo = ceo_similarities[0]["ceo"]
            strengths.append(f"Your approach aligns well with {top_ceo}'s leadership style")
        
        # Add strengths based on principles overlap
        if principles_overlap:
            strengths.append(f"You effectively applied key principles: {', '.join(principles_overlap)}")
        
        # Add improvement areas based on principles missing
        if principles_missing:
            improvement_areas.append(f"Consider incorporating these principles: {', '.join(principles_missing)}")
        
        # Add general feedback based on evaluation criteria
        feedback_parts = []
        for criterion in scenario.evaluation_criteria:
            # In a real implementation, this would be more sophisticated
            feedback_parts.append(f"Consider how your approach addresses: {criterion}")
        
        # Set feedback in submission
        submission.feedback = "\n\n".join(feedback_parts)
        submission.strengths = strengths
        submission.improvement_areas = improvement_areas
        
        return submission
    
    def _load_scenarios(self) -> Dict[str, TrainingScenario]:
        """Load training scenarios"""
        scenarios = {}
        
        # Load sample scenarios
        for scenario_data in SAMPLE_SCENARIOS:
            scenario = TrainingScenario(
                id=scenario_data["id"],
                title=scenario_data["title"],
                situation=scenario_data["situation"],
                context=scenario_data["context"],
                pillar=scenario_data["pillar"],
                difficulty=scenario_data["difficulty"],
                ceo_approaches=scenario_data["ceo_approaches"],
                principles=scenario_data["principles"],
                evaluation_criteria=scenario_data["evaluation_criteria"]
            )
            scenarios[scenario.id] = scenario
        
        # In a real implementation, this would load from a database
        return scenarios
