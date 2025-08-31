"""
Skill assessment module for the CEO training program.
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

from app.training.models import TraineeProfile, PillarSkill, SkillLevel
from app.engine.embeddings import get_embedding_engine

# Try to import repository
try:
    from app.repository.store import Repository, load_repository
    REPO_AVAILABLE = True
except ImportError:
    logger.warning("Repository module not available")
    REPO_AVAILABLE = False

# Assessment questions by pillar
ASSESSMENT_QUESTIONS = {
    "strategic_philosophy": [
        {
            "id": "sp_vision",
            "question": "How do you approach setting a long-term vision for your organization?",
            "skill_mapping": {
                "novice": "I focus on short-term goals and immediate problems",
                "developing": "I have some ideas about future direction but struggle to articulate them clearly",
                "proficient": "I can articulate a clear vision and connect it to current initiatives",
                "advanced": "I regularly communicate a compelling vision that guides decision-making",
                "expert": "I create transformative visions that inspire and align the entire organization"
            }
        },
        {
            "id": "sp_innovation",
            "question": "How do you approach innovation and new ideas?",
            "skill_mapping": {
                "novice": "I prefer established methods and proven approaches",
                "developing": "I'm open to new ideas but cautious about implementing them",
                "proficient": "I regularly seek out and evaluate new ideas for potential implementation",
                "advanced": "I create systems to encourage and test innovations throughout the organization",
                "expert": "I build a culture where breakthrough innovation is expected and rewarded"
            }
        },
        {
            "id": "sp_competition",
            "question": "How do you analyze and respond to competitive threats?",
            "skill_mapping": {
                "novice": "I focus on our own operations without much competitor analysis",
                "developing": "I track major competitors but react to their moves after the fact",
                "proficient": "I regularly analyze competitors and adjust our strategy accordingly",
                "advanced": "I anticipate competitive moves and prepare strategic responses in advance",
                "expert": "I redefine the competitive landscape to create new market opportunities"
            }
        },
        {
            "id": "sp_risk",
            "question": "How do you approach risk in strategic decisions?",
            "skill_mapping": {
                "novice": "I avoid risk whenever possible",
                "developing": "I take calculated risks in limited areas",
                "proficient": "I balance risk and reward across our strategic initiatives",
                "advanced": "I create portfolios of strategic bets with different risk profiles",
                "expert": "I transform uncertainty into strategic advantage through bold, calculated moves"
            }
        }
    ],
    "leadership_style": [
        {
            "id": "ls_hiring",
            "question": "What is your approach to hiring and building teams?",
            "skill_mapping": {
                "novice": "I hire based on immediate needs and availability",
                "developing": "I look for candidates with relevant experience and skills",
                "proficient": "I hire for both skills and cultural fit with clear criteria",
                "advanced": "I build diverse teams with complementary strengths and perspectives",
                "expert": "I create talent magnets that attract exceptional people who elevate the organization"
            }
        },
        {
            "id": "ls_culture",
            "question": "How do you shape organizational culture?",
            "skill_mapping": {
                "novice": "I don't focus much on culture; it develops organically",
                "developing": "I recognize culture issues but struggle to influence them systematically",
                "proficient": "I articulate values and reinforce them through recognition and feedback",
                "advanced": "I align systems, processes, and behaviors to intentionally shape culture",
                "expert": "I build distinctive cultures that become competitive advantages"
            }
        },
        {
            "id": "ls_communication",
            "question": "How would you describe your communication approach?",
            "skill_mapping": {
                "novice": "I communicate when issues arise or decisions are needed",
                "developing": "I share information regularly but without a systematic approach",
                "proficient": "I communicate consistently across multiple channels with clear messages",
                "advanced": "I tailor communication to different audiences and ensure two-way dialogue",
                "expert": "I create communication systems that build trust, alignment, and shared purpose"
            }
        },
        {
            "id": "ls_development",
            "question": "How do you approach developing your team members?",
            "skill_mapping": {
                "novice": "I focus on immediate performance rather than development",
                "developing": "I provide feedback and training when performance issues arise",
                "proficient": "I create development plans and provide regular coaching",
                "advanced": "I build development into daily work and create growth opportunities",
                "expert": "I create leadership factories that develop exceptional talent at all levels"
            }
        }
    ],
    "operational_cadence": [
        {
            "id": "oc_meetings",
            "question": "How do you structure and run meetings?",
            "skill_mapping": {
                "novice": "Meetings are scheduled as needed without much structure",
                "developing": "I have regular meetings but they often lack clear outcomes",
                "proficient": "I run efficient meetings with agendas and action items",
                "advanced": "I have a structured meeting system with different formats for different purposes",
                "expert": "My meeting system drives organizational rhythm and ensures execution excellence"
            }
        },
        {
            "id": "oc_decisions",
            "question": "How do you approach decision-making?",
            "skill_mapping": {
                "novice": "I make decisions based on intuition or immediate needs",
                "developing": "I gather some information but often decide under time pressure",
                "proficient": "I use a consistent process with relevant data and stakeholder input",
                "advanced": "I have different decision frameworks for different types of decisions",
                "expert": "I build decision systems that balance speed, quality, and organizational alignment"
            }
        },
        {
            "id": "oc_metrics",
            "question": "How do you use metrics and data?",
            "skill_mapping": {
                "novice": "I focus mainly on financial results after they happen",
                "developing": "I track some operational metrics but use them inconsistently",
                "proficient": "I use a balanced set of metrics to monitor performance",
                "advanced": "I use leading indicators and predictive metrics to drive decisions",
                "expert": "I build measurement systems that drive the right behaviors at all levels"
            }
        },
        {
            "id": "oc_execution",
            "question": "How do you ensure execution and follow-through?",
            "skill_mapping": {
                "novice": "I delegate tasks but don't have systematic follow-up",
                "developing": "I follow up on major initiatives but smaller items often slip",
                "proficient": "I have a tracking system for commitments and regular reviews",
                "advanced": "I build accountability into processes with clear ownership",
                "expert": "I create execution systems where accountability is embedded in the culture"
            }
        }
    ],
    "personal_ethos": [
        {
            "id": "pe_principles",
            "question": "How do you apply your personal values to leadership decisions?",
            "skill_mapping": {
                "novice": "I focus on practical considerations rather than values",
                "developing": "I have personal values but don't explicitly connect them to leadership",
                "proficient": "I consistently apply my values to major decisions",
                "advanced": "I articulate my values and use them to guide all aspects of leadership",
                "expert": "My authentic leadership principles create a distinctive legacy"
            }
        },
        {
            "id": "pe_learning",
            "question": "How do you approach learning and self-improvement?",
            "skill_mapping": {
                "novice": "I learn when necessary to solve immediate problems",
                "developing": "I occasionally seek learning opportunities but without a system",
                "proficient": "I have a regular learning practice across multiple domains",
                "advanced": "I systematically develop myself across technical, leadership, and personal dimensions",
                "expert": "I build learning systems for myself and the organization that drive continuous evolution"
            }
        },
        {
            "id": "pe_resilience",
            "question": "How do you handle setbacks and failures?",
            "skill_mapping": {
                "novice": "I try to avoid failure and find it difficult to recover from setbacks",
                "developing": "I can recover from setbacks but they significantly impact my confidence",
                "proficient": "I learn from failures and use them to improve",
                "advanced": "I anticipate potential failures and build resilience mechanisms",
                "expert": "I transform failures into strategic advantages and organizational learning"
            }
        },
        {
            "id": "pe_balance",
            "question": "How do you approach work-life balance and sustainability?",
            "skill_mapping": {
                "novice": "I prioritize work over personal needs until tasks are complete",
                "developing": "I recognize the importance of balance but struggle to maintain it",
                "proficient": "I have boundaries and practices that help maintain balance",
                "advanced": "I systematically manage energy and attention across all life domains",
                "expert": "I build sustainable performance systems for myself and the organization"
            }
        }
    ]
}

class AssessmentEngine:
    """Engine for assessing CEO skills and generating development recommendations"""
    
    def __init__(self):
        """Initialize the assessment engine"""
        self.embedding_engine = get_embedding_engine()
        self.repository = load_repository() if REPO_AVAILABLE else None
    
    def create_initial_profile(self, name: str, current_role: str, target_role: str, 
                               industry: Optional[str] = None, years_experience: int = 0) -> TraineeProfile:
        """Create an initial trainee profile with default skill levels"""
        trainee_id = name.lower().replace(" ", "_")
        
        return TraineeProfile(
            id=trainee_id,
            name=name,
            current_role=current_role,
            target_role=target_role,
            industry=industry,
            years_experience=years_experience
        )
    
    def process_assessment_answers(self, trainee_profile: TraineeProfile, 
                                  answers: Dict[str, str]) -> TraineeProfile:
        """Process assessment answers and update trainee profile with skill levels"""
        # Map of question ID to pillar
        question_to_pillar = {}
        for pillar, questions in ASSESSMENT_QUESTIONS.items():
            for question in questions:
                question_to_pillar[question["id"]] = pillar
        
        # Track skill levels by pillar
        pillar_levels = {
            "strategic_philosophy": [],
            "leadership_style": [],
            "operational_cadence": [],
            "personal_ethos": []
        }
        
        # Process each answer
        for question_id, answer in answers.items():
            if question_id not in question_to_pillar:
                logger.warning(f"Unknown question ID: {question_id}")
                continue
                
            pillar = question_to_pillar[question_id]
            
            # Find the question
            question_data = None
            for q in ASSESSMENT_QUESTIONS[pillar]:
                if q["id"] == question_id:
                    question_data = q
                    break
            
            if not question_data:
                logger.warning(f"Question data not found for ID: {question_id}")
                continue
            
            # Map answer to skill level
            skill_level = self._map_answer_to_skill_level(answer, question_data["skill_mapping"])
            pillar_levels[pillar].append(skill_level)
        
        # Calculate average skill level for each pillar
        for pillar, levels in pillar_levels.items():
            if not levels:
                continue
                
            # Convert skill levels to numeric values
            numeric_levels = [self._skill_level_to_numeric(level) for level in levels]
            avg_numeric = sum(numeric_levels) / len(numeric_levels)
            avg_level = self._numeric_to_skill_level(avg_numeric)
            
            # Update trainee profile
            if pillar == "strategic_philosophy":
                trainee_profile.strategic_philosophy.level = avg_level
            elif pillar == "leadership_style":
                trainee_profile.leadership_style.level = avg_level
            elif pillar == "operational_cadence":
                trainee_profile.operational_cadence.level = avg_level
            elif pillar == "personal_ethos":
                trainee_profile.personal_ethos.level = avg_level
        
        return trainee_profile
    
    def identify_role_models(self, trainee_profile: TraineeProfile, 
                            top_n: int = 3) -> List[Dict[str, Any]]:
        """Identify CEO role models based on trainee profile and preferences"""
        if not self.repository:
            logger.warning("Repository not available, cannot identify role models")
            return []
        
        # Create a profile text from the trainee profile
        profile_text = f"""
        Name: {trainee_profile.name}
        Current Role: {trainee_profile.current_role}
        Target Role: {trainee_profile.target_role}
        Industry: {trainee_profile.industry or 'Not specified'}
        Years Experience: {trainee_profile.years_experience}
        
        Strategic Philosophy: {trainee_profile.strategic_philosophy.level}
        Leadership Style: {trainee_profile.leadership_style.level}
        Operational Cadence: {trainee_profile.operational_cadence.level}
        Personal Ethos: {trainee_profile.personal_ethos.level}
        
        Learning Preferences: {', '.join(trainee_profile.learning_preferences)}
        """
        
        # Get embedding for trainee profile
        profile_embedding = self.embedding_engine.embed_text(profile_text)
        
        # Compare with CEOs in the repository
        ceo_similarities = []
        for ceo_name in self.repository.list_ceo_names():
            ceo_data = self.repository.get_ceo(ceo_name)
            if not ceo_data:
                continue
            
            # Create CEO text profile
            ceo_text = f"CEO: {ceo_name}\n"
            
            # Add strategic philosophy
            if "strategic_philosophy" in ceo_data:
                sp = ceo_data["strategic_philosophy"]
                for field, value in sp.items():
                    if value:
                        ceo_text += f"strategic_philosophy.{field}: {value}\n"
            
            # Add leadership style
            if "leadership_style" in ceo_data:
                ls = ceo_data["leadership_style"]
                for field, value in ls.items():
                    if value:
                        ceo_text += f"leadership_style.{field}: {value}\n"
            
            # Add operational cadence
            if "operational_cadence" in ceo_data:
                oc = ceo_data["operational_cadence"]
                for field, value in oc.items():
                    if value:
                        ceo_text += f"operational_cadence.{field}: {value}\n"
            
            # Add personal ethos
            if "personal_ethos" in ceo_data:
                pe = ceo_data["personal_ethos"]
                for field, value in pe.items():
                    if value:
                        ceo_text += f"personal_ethos.{field}: {value}\n"
            
            # Get embedding for CEO profile
            ceo_embedding = self.embedding_engine.embed_text(ceo_text)
            
            # Calculate similarity
            similarity = self.embedding_engine.compute_similarity(profile_embedding, ceo_embedding)
            
            ceo_similarities.append({
                "name": ceo_name,
                "similarity": similarity,
                "company": ceo_data.get("company", ""),
                "industry": ceo_data.get("industry", "")
            })
        
        # Sort by similarity (descending)
        ceo_similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        return ceo_similarities[:top_n]
    
    def generate_growth_recommendations(self, trainee_profile: TraineeProfile) -> Dict[str, List[str]]:
        """Generate growth recommendations based on trainee profile"""
        recommendations = {
            "strategic_philosophy": [],
            "leadership_style": [],
            "operational_cadence": [],
            "personal_ethos": []
        }
        
        # Strategic Philosophy recommendations
        sp_level = trainee_profile.strategic_philosophy.level
        if sp_level == SkillLevel.NOVICE:
            recommendations["strategic_philosophy"] = [
                "Read 'Good Strategy, Bad Strategy' by Richard Rumelt",
                "Practice articulating a vision for your team or organization",
                "Analyze your company's competitive position using Porter's Five Forces"
            ]
        elif sp_level == SkillLevel.DEVELOPING:
            recommendations["strategic_philosophy"] = [
                "Study Jeff Bezos' shareholder letters for long-term thinking examples",
                "Create a strategic plan with clear differentiators and trade-offs",
                "Identify and analyze emerging trends in your industry"
            ]
        elif sp_level == SkillLevel.PROFICIENT:
            recommendations["strategic_philosophy"] = [
                "Develop scenario planning for different possible futures",
                "Study Reed Hastings' Netflix transformation strategy",
                "Create a strategic narrative that connects vision to execution"
            ]
        elif sp_level == SkillLevel.ADVANCED:
            recommendations["strategic_philosophy"] = [
                "Study Andy Grove's strategic inflection points framework",
                "Develop a platform strategy that creates network effects",
                "Create a portfolio of strategic options with different time horizons"
            ]
        elif sp_level == SkillLevel.EXPERT:
            recommendations["strategic_philosophy"] = [
                "Study Steve Jobs' approach to creating new market categories",
                "Develop a framework for strategic reinvention",
                "Create a system for identifying and pursuing non-obvious opportunities"
            ]
        
        # Leadership Style recommendations
        ls_level = trainee_profile.leadership_style.level
        if ls_level == SkillLevel.NOVICE:
            recommendations["leadership_style"] = [
                "Read 'The Making of a Manager' by Julie Zhuo",
                "Practice active listening in one-on-one meetings",
                "Establish regular feedback sessions with your team"
            ]
        elif ls_level == SkillLevel.DEVELOPING:
            recommendations["leadership_style"] = [
                "Study Satya Nadella's cultural transformation at Microsoft",
                "Develop a personal leadership philosophy statement",
                "Create a hiring process that evaluates cultural fit and diversity"
            ]
        elif ls_level == SkillLevel.PROFICIENT:
            recommendations["leadership_style"] = [
                "Study Marc Benioff's V2MOM alignment system",
                "Develop a leadership development program for your team",
                "Create a communication strategy for organizational change"
            ]
        elif ls_level == SkillLevel.ADVANCED:
            recommendations["leadership_style"] = [
                "Study Indra Nooyi's stakeholder management approach",
                "Develop a succession planning system",
                "Create a culture measurement and reinforcement system"
            ]
        elif ls_level == SkillLevel.EXPERT:
            recommendations["leadership_style"] = [
                "Study Howard Schultz's approach to values-based leadership",
                "Develop a framework for leading through crisis and transformation",
                "Create a talent development system that builds future leaders"
            ]
        
        # Operational Cadence recommendations
        oc_level = trainee_profile.operational_cadence.level
        if oc_level == SkillLevel.NOVICE:
            recommendations["operational_cadence"] = [
                "Read 'The Effective Executive' by Peter Drucker",
                "Establish a weekly planning and review process",
                "Create agendas and action items for all meetings"
            ]
        elif oc_level == SkillLevel.DEVELOPING:
            recommendations["operational_cadence"] = [
                "Study Andy Grove's OKR system at Intel",
                "Develop a personal productivity system",
                "Create a dashboard of key metrics for your area"
            ]
        elif oc_level == SkillLevel.PROFICIENT:
            recommendations["operational_cadence"] = [
                "Study Jeff Bezos' meeting formats and decision-making processes",
                "Develop different meeting formats for different purposes",
                "Create a system for tracking and reviewing commitments"
            ]
        elif oc_level == SkillLevel.ADVANCED:
            recommendations["operational_cadence"] = [
                "Study Jamie Dimon's operational reviews at JPMorgan",
                "Develop a system for identifying and removing operational bottlenecks",
                "Create a forecasting and resource allocation process"
            ]
        elif oc_level == SkillLevel.EXPERT:
            recommendations["operational_cadence"] = [
                "Study Sam Walton's Saturday morning meeting ritual",
                "Develop an organizational rhythm that drives execution excellence",
                "Create a system for continuous process improvement"
            ]
        
        # Personal Ethos recommendations
        pe_level = trainee_profile.personal_ethos.level
        if pe_level == SkillLevel.NOVICE:
            recommendations["personal_ethos"] = [
                "Read 'Mindset' by Carol Dweck",
                "Establish a daily reflection practice",
                "Identify your core values and principles"
            ]
        elif pe_level == SkillLevel.DEVELOPING:
            recommendations["personal_ethos"] = [
                "Study Ray Dalio's Principles",
                "Develop a personal feedback system",
                "Create a learning plan across multiple domains"
            ]
        elif pe_level == SkillLevel.PROFICIENT:
            recommendations["personal_ethos"] = [
                "Study Warren Buffett's approach to integrity and reputation",
                "Develop a system for energy management across work and life",
                "Create a personal board of advisors"
            ]
        elif pe_level == SkillLevel.ADVANCED:
            recommendations["personal_ethos"] = [
                "Study Satya Nadella's growth mindset transformation",
                "Develop a framework for ethical decision-making",
                "Create a system for continuous self-reinvention"
            ]
        elif pe_level == SkillLevel.EXPERT:
            recommendations["personal_ethos"] = [
                "Study Yvon Chouinard's values-based leadership at Patagonia",
                "Develop a legacy plan that extends beyond your tenure",
                "Create a system for developing wisdom from experience"
            ]
        
        return recommendations
    
    def _map_answer_to_skill_level(self, answer: str, skill_mapping: Dict[str, str]) -> SkillLevel:
        """Map an answer to a skill level based on the closest match"""
        if not answer:
            return SkillLevel.NOVICE
        
        # If the answer exactly matches one of the skill descriptions, return that level
        for level, description in skill_mapping.items():
            if answer == description:
                return SkillLevel(level)
        
        # Otherwise, use embedding similarity to find the closest match
        answer_embedding = self.embedding_engine.embed_text(answer)
        
        best_similarity = -1
        best_level = SkillLevel.NOVICE
        
        for level, description in skill_mapping.items():
            description_embedding = self.embedding_engine.embed_text(description)
            similarity = self.embedding_engine.compute_similarity(answer_embedding, description_embedding)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_level = SkillLevel(level)
        
        return best_level
    
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
    
    def _numeric_to_skill_level(self, value: float) -> SkillLevel:
        """Convert numeric value to skill level"""
        if value < 1.5:
            return SkillLevel.NOVICE
        elif value < 2.5:
            return SkillLevel.DEVELOPING
        elif value < 3.5:
            return SkillLevel.PROFICIENT
        elif value < 4.5:
            return SkillLevel.ADVANCED
        else:
            return SkillLevel.EXPERT
