import numpy as np
import random
from typing import List, Dict

SKILL_DIFFICULTY = {
    "html": 1, "css": 1, "git": 1, "bash": 1,
    "javascript": 2, "python": 2, "bootstrap": 1, "tailwind": 1,
    "typescript": 3, "react": 3, "nodejs": 3, "vue": 3, "angular": 3,
    "django": 3, "flask": 2, "fastapi": 2, "express": 3,
    "postgresql": 3, "mongodb": 2, "redis": 3, "mysql": 2,
    "docker": 4, "aws": 4, "kubernetes": 5, "terraform": 4,
    "machine learning": 4, "deep learning": 5, "nlp": 4,
    "tensorflow": 4, "pytorch": 4, "scikit-learn": 3,
    "pandas": 2, "numpy": 2, "data visualization": 2,
    "graphql": 3, "microservices": 4, "ci/cd": 3,
    "nextjs": 3, "rest api": 2, "agile": 1, "scrum": 1,
    "linux": 2, "figma": 2, "communication": 1, "leadership": 2,
    "problem solving": 1, "teamwork": 1, "project management": 2
}

SKILL_LEARNING_TIME = {
    "html": 1, "css": 1, "git": 1, "bash": 1, "agile": 1,
    "scrum": 1, "communication": 1, "teamwork": 1, "problem solving": 1,
    "bootstrap": 1, "tailwind": 1,
    "javascript": 4, "python": 4, "numpy": 2, "pandas": 2,
    "flask": 2, "fastapi": 2, "mysql": 2, "mongodb": 2,
    "rest api": 2, "linux": 2, "figma": 2, "leadership": 2,
    "data visualization": 2, "project management": 2,
    "typescript": 3, "react": 4, "nodejs": 3, "vue": 3,
    "angular": 4, "django": 3, "express": 3, "postgresql": 3,
    "redis": 3, "nextjs": 3, "graphql": 3, "scikit-learn": 3,
    "ci/cd": 3,
    "docker": 4, "aws": 6, "machine learning": 8, "nlp": 6,
    "tensorflow": 5, "pytorch": 5, "kubernetes": 6,
    "terraform": 4, "deep learning": 8, "microservices": 4
}

SKILL_PREREQUISITES = {
    "react": ["javascript", "html", "css"],
    "nextjs": ["react", "javascript"],
    "angular": ["javascript", "typescript", "html", "css"],
    "vue": ["javascript", "html", "css"],
    "typescript": ["javascript"],
    "nodejs": ["javascript"],
    "express": ["nodejs", "javascript"],
    "django": ["python"],
    "fastapi": ["python"],
    "flask": ["python"],
    "tensorflow": ["python", "numpy", "pandas"],
    "pytorch": ["python", "numpy"],
    "scikit-learn": ["python", "numpy", "pandas"],
    "machine learning": ["python", "numpy", "pandas"],
    "deep learning": ["machine learning", "tensorflow"],
    "nlp": ["python", "machine learning"],
    "kubernetes": ["docker"],
    "nextjs": ["react"],
    "graphql": ["rest api"],
    "ci/cd": ["git", "docker"],
    "terraform": ["aws", "docker"],
    "data visualization": ["python", "pandas"],
}

class SkillGapEnvironment:
    def __init__(self, missing_skills: List[str], user_skills: List[str]):
        self.missing_skills = [s.lower() for s in missing_skills]
        self.user_skills = [s.lower() for s in user_skills]
        self.state = set(self.user_skills)
        self.target_skills = set(self.missing_skills)
        self.learned_skills = []

    def get_state(self) -> frozenset:
        return frozenset(self.state)

    def get_available_actions(self) -> List[str]:
        available = []
        for skill in self.missing_skills:
            if skill in self.state:
                continue
            prerequisites = SKILL_PREREQUISITES.get(skill, [])
            if all(prereq in self.state for prereq in prerequisites):
                available.append(skill)
        return available if available else [
            s for s in self.missing_skills if s not in self.state
        ]

    def calculate_reward(self, skill: str) -> float:
        from services.gap_analyzer import get_skill_weight
        base_reward = get_skill_weight(skill) * 10

        difficulty = SKILL_DIFFICULTY.get(skill, 3)
        difficulty_bonus = (6 - difficulty) * 2

        prerequisites = SKILL_PREREQUISITES.get(skill, [])
        prereq_penalty = sum(
            5 for p in prerequisites if p not in self.state
        )

        unlocks = sum(
            1 for s, prereqs in SKILL_PREREQUISITES.items()
            if skill in prereqs and s in self.target_skills
        )
        unlock_bonus = unlocks * 5

        return base_reward + difficulty_bonus + unlock_bonus - prereq_penalty

    def step(self, skill: str):
        reward = self.calculate_reward(skill)
        self.state.add(skill)
        self.learned_skills.append(skill)
        done = self.target_skills.issubset(self.state)
        return self.get_state(), reward, done

class QLearningAgent:
    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        epsilon: float = 0.3,
        episodes: int = 200
    ):
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.episodes = episodes
        self.q_table = {}

    def get_q_value(self, state: frozenset, action: str) -> float:
        return self.q_table.get((state, action), 0.0)

    def choose_action(
        self, state: frozenset, available_actions: List[str]
    ) -> str:
        if not available_actions:
            return None
        if random.random() < self.epsilon:
            return random.choice(available_actions)
        q_values = {
            a: self.get_q_value(state, a) for a in available_actions
        }
        return max(q_values, key=q_values.get)

    def update_q_value(
        self,
        state: frozenset,
        action: str,
        reward: float,
        next_state: frozenset,
        next_actions: List[str]
    ):
        current_q = self.get_q_value(state, action)
        if next_actions:
            max_next_q = max(
                self.get_q_value(next_state, a) for a in next_actions
            )
        else:
            max_next_q = 0.0
        new_q = current_q + self.lr * (
            reward + self.gamma * max_next_q - current_q
        )
        self.q_table[(state, action)] = new_q

    def train(self, missing_skills: List[str], user_skills: List[str]):
        for episode in range(self.episodes):
            env = SkillGapEnvironment(missing_skills, user_skills)
            self.epsilon = max(0.05, 0.3 * (1 - episode / self.episodes))
            done = False
            steps = 0
            while not done and steps < len(missing_skills) * 3:
                state = env.get_state()
                actions = env.get_available_actions()
                if not actions:
                    break
                action = self.choose_action(state, actions)
                if not action:
                    break
                next_state, reward, done = env.step(action)
                next_actions = env.get_available_actions()
                self.update_q_value(
                    state, action, reward, next_state, next_actions
                )
                steps += 1

def generate_learning_roadmap(
    missing_skills: List[str],
    user_skills: List[str],
    target_role: str
) -> dict:
    if not missing_skills:
        return {
            "target_role": target_role,
            "message": "Congratulations! You have all the required skills.",
            "roadmap": [],
            "total_weeks": 0
        }

    # Sort skills by difficulty (easy first) to start from basics
    sorted_by_difficulty = sorted(
        missing_skills,
        key=lambda s: SKILL_DIFFICULTY.get(s.lower(), 3)
    )

    agent = QLearningAgent(episodes=300)
    agent.train(sorted_by_difficulty, user_skills)

    env = SkillGapEnvironment(sorted_by_difficulty, user_skills)
    ordered_skills = []
    done = False
    steps = 0

    while not done and steps < len(sorted_by_difficulty) * 2:
        state = env.get_state()
        actions = env.get_available_actions()
        if not actions:
            break
        q_values = {a: agent.get_q_value(state, a) for a in actions}
        best_action = max(q_values, key=q_values.get)
        _, _, done = env.step(best_action)
        ordered_skills.append(best_action)
        steps += 1

    # Ensure all skills are included
    for skill in sorted_by_difficulty:
        if skill not in ordered_skills:
            ordered_skills.append(skill)

    roadmap = []
    current_week = 1

    for i, skill in enumerate(ordered_skills):
        weeks_needed = SKILL_LEARNING_TIME.get(skill, 3)
        difficulty = SKILL_DIFFICULTY.get(skill, 3)
        prerequisites = SKILL_PREREQUISITES.get(skill, [])
        known_prereqs = [p for p in prerequisites if p in user_skills]
        missing_prereqs = [p for p in prerequisites if p not in user_skills and p not in ordered_skills[:i]]

        if difficulty <= 2:
            priority = "low"
        elif difficulty <= 3:
            priority = "medium"
        else:
            priority = "high"

        roadmap.append({
            "step": i + 1,
            "skill": skill,
            "priority": priority,
            "difficulty": difficulty,
            "difficulty_label": (
                "Beginner" if difficulty <= 2 else
                "Intermediate" if difficulty <= 3 else
                "Advanced"
            ),
            "estimated_weeks": weeks_needed,
            "start_week": current_week,
            "end_week": current_week + weeks_needed - 1,
            "prerequisites": prerequisites,
            "known_prerequisites": known_prereqs,
            "missing_prerequisites": missing_prereqs,
            "q_value": round(agent.get_q_value(frozenset(), skill), 2)
        })
        current_week += weeks_needed

    total_weeks = sum(item["estimated_weeks"] for item in roadmap)
    total_months = round(total_weeks / 4, 1)

    return {
        "target_role": target_role,
        "total_skills_to_learn": len(ordered_skills),
        "total_weeks": total_weeks,
        "total_months": total_months,
        "message": f"Your personalized roadmap to become a {target_role} in ~{total_months} months",
        "roadmap": roadmap
    }