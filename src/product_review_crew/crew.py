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
            temperature=0,
            model_name="mixtral-8x7b-32768"
        )

    @agent
    def product_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['product_researcher'],
            llm=self.groq_llm
        )

    @agent
    def keyword_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['keyword_researcher'],
            llm=self.groq_llm
        )

    @agent
    def review_drafter(self) -> Agent:
        return Agent(
            config=self.agents_config['review_drafter'],
            llm=self.groq_llm
        )

    @agent
    def draft_critique(self) -> Agent:
        return Agent(
            config=self.agents_config['draft_critique'],
            llm=self.groq_llm
        )

    @agent
    def final_drafter(self) -> Agent:
        return Agent(
            config=self.agents_config['final_drafter'],
            llm=self.groq_llm
        )

    @task
    def product_researcher_task(self) -> Task:
        return Task(
            config=self.tasks_config['product_researcher_task'],
            agent=self.product_researcher()
        )

    @task
    def keyword_researcher_task(self) -> Task:
        return Task(
            config=self.tasks_config['keyword_researcher_task'],
            agent=self.keyword_researcher()
        )

    @task
    def review_drafter_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_drafter_task'],
            agent=self.review_drafter()
        )

    @task
    def draft_critique_task(self) -> Task:
        return Task(
            config=self.tasks_config['draft_critique_task'],
            agent=self.draft_critique()
        )

    @task
    def final_drafter_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_drafter_task'],
            agent=self.final_drafter()
        )

    @crew
    def crew(self, product_type) -> Crew:
        """Create crew for Product Review"""
        if product_type == 'product':
            return Crew(
                agents=[
                    self.product_researcher(),
                    self.keyword_researcher(),
                    self.review_drafter(),
                    self.draft_critique(),
                    self.final_drafter(),
                    ],
                tasks=[
                    self.product_researcher_task(),
                    self.keyword_researcher_task(),
                    self.review_drafter_task(),
                    self.draft_critique_task(),
                    self.final_drafter_task(),
                    ],
                process=Process.sequential,
                verbose=2
            )
        elif product_type == 'test':
            return Crew(
                agents=[
                    self.keyword_researcher(),
                    ],
                tasks=[
                    self.keyword_researcher_task(),
                    ],
                process=Process.sequential,
                verbose=2
            )
