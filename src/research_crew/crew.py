from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_groq import ChatGroq
import random


@CrewBase
class ProductReviewCrew():
    """Crew for product review"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        self.model_names = [
            "mixtral-8x7b-32768",
            "llama3-70b-8192",
            # "llama3-8b-8192",
            ]

    def agent_init(self, agent_name, temperature=0.2):
        chosen_model = random.choice(self.model_names)
        groq_llm = ChatGroq(
            temperature=temperature,
            model_name=chosen_model
        )
        return Agent(
            config=self.agents_config[agent_name],
            llm=groq_llm
        )

    def task_init(self, task_name, agent_name):
        return Task(
            config=self.tasks_config[task_name],
            agent=agent_name
        )
        
    @agent
    def product_researcher(self) -> Agent:
        return self.agent_init('product_researcher')

    @task
    def product_researcher_task(self) -> Task:
        return self.task_init(
            'product_researcher_task',
            self.product_researcher())

    @crew
    def crew(self, task) -> Crew:
        return Crew(
            agents=[
                self.product_researcher(),
                ],
            tasks=[
                self.product_researcher_task(),
                ],
            process=Process.sequential,
            verbose=2
        )