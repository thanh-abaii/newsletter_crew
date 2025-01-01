from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
# from typing import Dict, List, Tuple, Union
# from langchain_core.agents import AgentFinish
from langchain_openai import ChatOpenAI

# THAY import Search() bằng CachedSearch()
from newsletter_crew.tools.cached_search import CachedSearch
from newsletter_crew.tools.research import FindSimilar, GetContents

import datetime
import os


@CrewBase
class NewsletterGenCrew:
    """Newsletter crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def llm(self):
        # Vẫn dùng model cũ
        llm = ChatOpenAI(api_key=os.environ['OPENAI_API_KEY'], model='gpt-4o-mini')
        return llm

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            # Đổi chỗ này: thay Search() bằng CachedSearch()
            tools=[CachedSearch(), FindSimilar(), GetContents()],
            verbose=True,
            llm=self.llm(),
        )

    @agent
    def editor(self) -> Agent:
        return Agent(
            config=self.agents_config["editor"],
            verbose=True,
            # Nếu bạn muốn editor cũng hưởng lợi từ cache, thêm CachedSearch() ở đây
            tools=[CachedSearch(), FindSimilar(), GetContents()],
            llm=self.llm(),
        )

    @agent
    def designer(self) -> Agent:
        return Agent(
            config=self.agents_config["designer"],
            verbose=True,
            llm=self.llm(),
            allow_delegation=False,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.researcher(),
            output_file=f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}_research_task.md",
        )

    @task
    def edit_task(self) -> Task:
        return Task(
            config=self.tasks_config["edit_task"],
            agent=self.editor(),
            output_file=f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}_edit_task.md",
        )

    @task
    def newsletter_task(self) -> Task:
        return Task(
            config=self.tasks_config["newsletter_task"],
            agent=self.designer(),
            output_file=f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}_newsletter.html",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Newsletter crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
