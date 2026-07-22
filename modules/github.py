from __future__ import annotations

from typing import Any

from config import Config
from core.utils import Utils


class GitHubModule:
    name = "github"

    SEARCH_QUERIES = [
        "domain:{domain}",
        "{domain} email",
        "{domain} api",
        "{domain} config",
        "{domain} docker",
        "{domain} nginx",
        "{domain} .env",
    ]

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {"repositories": [], "code_results": [], "total_count": 0}
        token = config.api.github_token
        if not token:
            result["error"] = "No GitHub token configured"
            result["search_queries"] = [
                f"site:github.com {domain}",
                f"site:github.com {domain} config",
                f"site:github.com {domain} .env",
            ]
            return result

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        client = Utils.create_client(config.timeout)
        try:
            for query in self.SEARCH_QUERIES:
                q = query.format(domain=domain)
                try:
                    response = Utils.safe_get(
                        client,
                        "https://api.github.com/search/code",
                        headers=headers,
                        params={"q": q, "per_page": 10},
                    )
                    if response and response.status_code == 200:
                        data = response.json()
                        items = data.get("items", [])
                        for item in items[:5]:
                            entry = {
                                "repository": item.get("repository", {}).get("full_name", ""),
                                "path": item.get("path", ""),
                                "url": item.get("html_url", ""),
                            }
                            result["code_results"].append(entry)
                            repo_full = item.get("repository", {}).get("full_name", "")
                            if repo_full and repo_full not in result["repositories"]:
                                result["repositories"].append(repo_full)
                    elif response and response.status_code == 403:
                        result["error"] = "GitHub API rate limit exceeded"
                        break
                except Exception:
                    pass

            repo_search_response = Utils.safe_get(
                client,
                "https://api.github.com/search/repositories",
                headers=headers,
                params={"q": domain, "per_page": 10, "sort": "stars"},
            )
            if repo_search_response and repo_search_response.status_code == 200:
                repo_data = repo_search_response.json()
                for item in repo_data.get("items", []):
                    repo = {
                        "name": item.get("full_name", ""),
                        "description": item.get("description", ""),
                        "stars": item.get("stargazers_count", 0),
                        "url": item.get("html_url", ""),
                        "language": item.get("language", ""),
                    }
                    if "repositories_list" not in result:
                        result["repositories_list"] = []
                    seen_repos = {r["name"] for r in result["repositories_list"]}
                    if repo["name"] not in seen_repos:
                        result["repositories_list"].append(repo)

            result["total_count"] = len(result["code_results"])
        except Exception as e:
            result["error"] = str(e)
        finally:
            client.close()
        return result
