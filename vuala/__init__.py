#! /usr/bin/env python3

from openai import OpenAI
import os
import pprint
import siteclient as siteclient
import getpass
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from vuala.agent import Agent, get_test_plans, get_workflows
from vuala.output import write_markdown
import mock.webacademy as webacademy

set_llm_cache(SQLiteCache(database_path=".langchain.db"))
# set_debug(True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pp = pprint.PrettyPrinter(indent=2)

"""
Vulnerability Understanding and Analysis Language Agent
"""


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


_set_env("OPENAI_API_KEY")


def main():
    har = webacademy.har()
    workflows = get_workflows(har)
    write_markdown(workflows.markdown())

    ###
    client = webacademy.Mock("webacademy.com")
    ###

    for workflow in workflows.workflows:
        if workflow.can_be_vulnerable:
            test_plans = get_test_plans(workflow, har)

            for test_plan in test_plans.test_plans:
                write_markdown(workflow.markdown())
                write_markdown(test_plan.markdown())
                agent = Agent(workflow, test_plan, har, client)
                agent.test()


if __name__ == "__main__":
    main()
