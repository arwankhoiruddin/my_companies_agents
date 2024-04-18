from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_groq import ChatGroq


@CrewBase
class SupplementReviewCrew():
    """Crew for supplement review"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self) -> None:
        self.groq_llm = ChatGroq(
            temperature=0,
            model_name="mixtral-8x7b-32768"
        )

    @agent
    def product_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['product_researcher'],
            llm=self.groq_llm
        )

    @task
    def product_researcher_task(self) -> Task:
        return Task(
            config=self.tasks_config['product_researcher_task'],
            agent=self.product_researcher()
        )

    @crew
    def crew(self) -> Crew:
        """Create crew for Supplement Review"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2
        )
