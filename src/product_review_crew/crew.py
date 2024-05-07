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
    
    @agent
    def article_expander(self) -> Agent:
        return self.agent_init('article_expander')
    
    @agent
    def final_formatter(self) -> Agent:
        return self.agent_init('final_formatter')
    
    @agent
    def explanation_provider(self) -> Agent:
        return self.agent_init('explanation_provider')
    
    @agent
    def journal_reader(self) -> Agent:
        return self.agent_init('journal_reader', 0)
    
    @agent
    def text_rewriter(self) -> Agent:
        return self.agent_init('text_rewriter')

    @task
    def product_researcher_task(self) -> Task:
        return self.task_init(
            'product_researcher_task',
            self.product_researcher())

    @task
    def keyword_researcher_task(self) -> Task:
        return self.task_init(
            'keyword_researcher_task',
            self.keyword_researcher())

    @task
    def review_drafter_task(self) -> Task:
        return self.task_init(
            'review_drafter_task',
            self.review_drafter())

    @task
    def draft_critique_task(self) -> Task:
        return self.task_init(
            'draft_critique_task',
            self.draft_critique())

    @task
    def final_drafter_task(self) -> Task:
        return self.task_init(
            'final_drafter_task',
            self.final_drafter())

    @task
    def problem_identifier_task(self) -> Task:
        return self.task_init(
            'problem_identifier_task',
            self.problem_identifier())

    @task
    def problem_keyword_researcher_task(self) -> Task:
        return self.task_init(
            'problem_keyword_researcher_task',
            self.problem_keyword_researcher())

    @task
    def problem_expert_task(self) -> Task:
        return self.task_init(
            'problem_expert_task',
            self.problem_expert())
    
    @task
    def article_expander_task(self) -> Task:
        return self.task_init(
            'article_expander_task',
            self.article_expander())
    
    @task
    def final_formatter_task(self) -> Task:
        return self.task_init(
            'final_formatter_task',
            self.final_formatter())
    
    @task
    def explanation_provider_task(self) -> Task:
        return self.task_init(
            'explanation_provider_task',
            self.explanation_provider())
        
    @task
    def journal_reader_task(self) -> Task:
        return self.task_init(
            'journal_reader_task',
            self.journal_reader())
        
    @task
    def text_rewriting_task(self) -> Task:
        return self.task_init(
            'text_rewriting_task',
            self.text_rewriter())
        
    @agent
    def article_writer(self) -> Agent:
        return self.agent_init('article_writer')
    
    @task
    def article_writing_task(self) -> Task:
        return self.task_init(
            'article_writing_task',
            self.article_writer())

    @crew
    def crew(self, task) -> Crew:
        if task == 'article_seed':
            return Crew(
                agents=[
                    self.problem_identifier(),
                    self.problem_keyword_researcher(),
                    self.article_writer(),
                    # self.problem_expert(),
                    # self.final_formatter(),
                    # self.text_rewriter(),
                    ],
                tasks=[
                    self.problem_identifier_task(),
                    self.problem_keyword_researcher_task(),
                    self.article_writing_task(),
                    # self.problem_expert_task(),
                    # self.final_formatter_task(),
                    # self.text_rewriting_task(),
                    ],
                process=Process.sequential,
                verbose=2
            )
        elif task == 'explain':
            return Crew(
                agents=[
                    self.explanation_provider(),
                    ],
                tasks=[
                    self.explanation_provider_task(),
                    ],
                process=Process.sequential,
                verbose=2
            )
        elif task == 'test':
            return Crew(
                agents=[
                    self.article_writer(),
                    ],
                tasks=[
                    self.article_writing_task(),
                    ],
                process=Process.sequential,
                verbose=2
            )
