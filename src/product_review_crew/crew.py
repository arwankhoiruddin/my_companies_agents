from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_groq import ChatGroq


@CrewBase
class ProductReviewCrew():
    """Crew for product review"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        self.groq_llm = ChatGroq(
            temperature=0.5,
            model_name='llama3-70b-8192'  # 'llama3-8b-8192'  # "mixtral-8x7b-32768"
        )
        
    def agent_init(self, agent_name):
        return Agent(
            config=self.agents_config[agent_name],
            llm=self.groq_llm
        )
        
    def task_init(self, task_name, agent_name):
        return Task(
            config=self.tasks_config[task_name],
            agent=agent_name
        )
        

    @agent
    def product_researcher(self) -> Agent:
        return self.agent_init('product_researcher')

    @agent
    def keyword_researcher(self) -> Agent:
        return self.agent_init('keyword_researcher')

    @agent
    def review_drafter(self) -> Agent:
        return self.agent_init('review_drafter')

    @agent
    def draft_critique(self) -> Agent:
        return self.agent_init('draft_critique')

    @agent
    def final_drafter(self) -> Agent:
        return self.agent_init('final_drafter')

    @agent
    def problem_identifier(self) -> Agent:
        return self.agent_init('problem_identifier')

    @agent
    def problem_keyword_researcher(self) -> Agent:
        return self.agent_init('problem_keyword_researcher')
    
    @agent
    def problem_expert(self) -> Agent:
        return self.agent_init('problem_expert')

    @task
    def product_researcher_task(self) -> Task:
        return self.task_init('product_researcher_task', self.product_researcher())

    @task
    def keyword_researcher_task(self) -> Task:
        return self.task_init('keyword_researcher_task', self.keyword_researcher())

    @task
    def review_drafter_task(self) -> Task:
        return self.task_init('review_drafter_task', self.review_drafter())

    @task
    def draft_critique_task(self) -> Task:
        return self.task_init('draft_critique_task', self.draft_critique())

    @task
    def final_drafter_task(self) -> Task:
        return self.task_init('final_drafter_task', self.final_drafter())

    @task
    def problem_identifier_task(self) -> Task:
        return self.task_init('problem_identifier_task', self.problem_identifier())

    @task
    def problem_keyword_researcher_task(self) -> Task:
        return self.task_init('problem_keyword_researcher_task', self.problem_keyword_researcher())

    @task
    def problem_expert_task(self) -> Task:
        return self.task_init('problem_expert_task', self.problem_expert())

    @crew
    def crew(self, task) -> Crew:
        if task == 'soft_selling':
            return Crew(
                agents=[
                    self.problem_identifier(),
                    self.problem_keyword_researcher(),
                    self.keyword_researcher(),
                    self.problem_expert(),
                    ],
                tasks=[
                    self.problem_identifier_task(),
                    self.problem_keyword_researcher_task(),
                    self.keyword_researcher_task(),
                    self.problem_expert_task(),
                    ],

                process=Process.sequential,
                verbose=2
            )
        elif task == 'test':
            return Crew(
                agents=[
                    self.problem_identifier(),
                    self.problem_keyword_researcher(),
                    self.problem_expert(),
                    # self.soft_seller(),
                    ],
                tasks=[
                    self.problem_identifier_task(),
                    self.problem_keyword_researcher_task(),
                    self.problem_expert_task(),
                    # self.soft_seller_task(),
                    ],
                process=Process.sequential,
                verbose=2
            )
