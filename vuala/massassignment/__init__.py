from devtools import pprint
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
import vuala.massassignment.reproduce_login as reproduce_login
from vuala.massassignment.common import portuguese_har, standard_har, scopes_har, Client
import vuala.massassignment.generate_and_test as generate_and_test
import vuala.massassignment.extract_login as extract_login
from vuala.output import write_markdown
import vuala.massassignment.get_resources as get_resources

set_llm_cache(SQLiteCache(database_path=".massassignment.db"))


def main():
    har, client = scopes_har()
    related_requests = extract_login.invoke(har["log"]["entries"])
    pprint(related_requests)
    reproduced = reproduce_login.invoke(client, related_requests.entries)
    pprint(reproduced)
    resources = get_resources.invoke(related_requests.entries)
    pprint(resources)
    exploit = generate_and_test.invoke(
        client,
        reproduced,
        related_requests.permission_verification,
        resources.resources,
    )
    write_markdown("### ✅ Vulnerability found")
    write_markdown(exploit.markdown())


if __name__ == "__main__":
    main()
