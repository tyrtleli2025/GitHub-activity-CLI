import requests
import json
import argparse

def get_user_data(username):
    url = f"https://api.github.com/users/{username}/events"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def main():
    parser = argparse.ArgumentParser(
        description="Show recent GitHub activity for a user"
    )
    parser.add_argument("username", help="GitHub username to fetch events for")
    parser.add_argument("-n", "--limit", type=int, default=10,
                        help="number of events to show (default: 10)")
    args = parser.parse_args()

    events = get_user_data(args.username)
    if not events:
        print("No events found or request failed.")
        return


    for evt in events:  
        evt_type  = evt.get("type")
        repo_name = evt.get("repo", {}).get("name")

        line = f"{evt_type} on {repo_name or '(unknown repo)'}"
        payload = evt.get("payload", {})

        if evt_type == "IssuesEvent":
            action = payload.get("action")
            if action and repo_name:
                line = f"{action.capitalize()} an issue in {repo_name}"

        elif evt_type == "PushEvent":
            count = payload.get("size")
            if isinstance(count, int) and count > 0 and repo_name:
                line = f"Pushed {count} commit{'s' if count != 1 else ''} to {repo_name}"
            else:
                line = f"Pushed to {repo_name or '(unknown repo)'}"

        elif evt_type == "PullRequestEvent":
            action = payload.get("action")
            pr_num = payload.get("number")
            pr = payload.get("pull_request", {}) or {}
            title = pr.get("title")
            merged = pr.get("merged")  # bool or None

            if action and repo_name and pr_num:
                verb = "Merged" if (action == "closed" and merged) else action.capitalize()
                if title:
                    line = f"{verb} PR #{pr_num} in {repo_name}: {title}"
                else:
                    line = f"{verb} PR #{pr_num} in {repo_name}"

        elif evt_type == "IssueCommentEvent":
            comment_body = (payload.get("comment") or {}).get("body")
            if comment_body:
                snippet = (comment_body[:60] + "…") if len(comment_body) > 60 else comment_body
                line = f"Commented: {snippet}"
        elif evt_type == "WatchEvent":
            action = payload.get("action")  # usually "started"
            if repo_name:
                if action:
                    line = f"{action.capitalize()} {repo_name}"
                else:
                    line = f"Starred {repo_name}"  # fallback

        elif evt_type == "ForkEvent":
            forkee = payload.get("forkee") or {}
            fork_full_name = forkee.get("full_name")  # e.g., "yourname/repo"
            if repo_name and fork_full_name:
                line = f"Forked {repo_name} to {fork_full_name}"
            elif repo_name:
                line = f"Forked {repo_name}"
            # else keep the default line

        elif evt_type == "CreateEvent":
            # payload has:
            #   ref_type: "repository" | "branch" | "tag"
            #   ref: name of branch/tag (None for repository creation)
            ref_type = payload.get("ref_type")
            ref = payload.get("ref")

            if ref_type == "repository" and repo_name:
                line = f"Created repository {repo_name}"
            elif ref_type in ("branch", "tag"):
                name = ref or "(unnamed)"
                if repo_name:
                    line = f"Created {ref_type} {name} in {repo_name}"
                else:
                    line = f"Created {ref_type} {name}"
            # else: keep the default 'line'



        print(line)

if __name__== "__main__": 
    main()