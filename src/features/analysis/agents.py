from crewai import Agent
from .prompts import (
    TECH_LEAD_ROLE, TECH_LEAD_GOAL, TECH_LEAD_BACKSTORY,
    PSYCHOLOGIST_ROLE, PSYCHOLOGIST_GOAL, PSYCHOLOGIST_BACKSTORY,
    ADVISOR_ROLE, ADVISOR_GOAL, ADVISOR_BACKSTORY,
    MENTOR_ROLE, MENTOR_GOAL, MENTOR_BACKSTORY
)
from .tools import CareerAnalysisTools

def create_tech_lead_agent(llm):
    """資深技術評估專家 Agent"""
    return Agent(
        role=TECH_LEAD_ROLE,
        goal=TECH_LEAD_GOAL,
        backstory=TECH_LEAD_BACKSTORY,
        tools=[CareerAnalysisTools.calculate_tech_vectors],
        verbose=True,
        llm=llm,
        allow_delegation=False
    )

def create_psychologist_agent(llm):
    """認知心理學家 Agent"""
    return Agent(
        role=PSYCHOLOGIST_ROLE,
        goal=PSYCHOLOGIST_GOAL,
        backstory=PSYCHOLOGIST_BACKSTORY,
        tools=[],
        verbose=True,
        llm=llm,
        allow_delegation=False
    )

def create_career_advisor_agent(llm):
    """職涯策略顧問 Agent"""
    return Agent(
        role=ADVISOR_ROLE,
        goal=ADVISOR_GOAL,
        backstory=ADVISOR_BACKSTORY,
        tools=[],
        verbose=True,
        llm=llm,
        allow_delegation=False
    )

def create_discovery_mentor_agent(llm):
    """轉職潛力挖掘導師 Agent (Entry Level 用)"""
    return Agent(
        role=MENTOR_ROLE,
        goal=MENTOR_GOAL,
        backstory=MENTOR_BACKSTORY,
        tools=[],
        verbose=True,
        llm=llm,
        allow_delegation=False
    )
