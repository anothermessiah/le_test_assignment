import csv
import requests

OWNER = "appwrite"
REPO = "appwrite"


def fetch_open_prs(owner: str, repo: str):
    """Fetch all open pull requests for given repo (with pagination)."""
    all_prs = []
    page = 1

    while True:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            params={
                "state": "open",
                "per_page": 100,  # max per page
                "page": page,
            },
            headers={
                "Accept": "application/vnd.github+json",
                # Add token here if you hit rate limits:
                # "Authorization": "Bearer YOUR_TOKEN",
            },
            timeout=10,
        )
        response.raise_for_status()
        batch = response.json()

        if not batch:
            break

        all_prs.extend(batch)
        page += 1

    return all_prs


def write_prs_to_csv(prs, filename: str):
    """Write PR list to CSV: name, created_at, author."""
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["name", "created_at", "author"])

        for pr in prs:
            title = pr.get("title", "")
            created_at = pr.get("created_at", "")
            author = pr.get("user", {}).get("login", "")
            writer.writerow([title, created_at, author])


def main():
    prs = fetch_open_prs(OWNER, REPO)
    print(f"Open PRs: {len(prs)}")

    output_file = "open_prs.csv"
    write_prs_to_csv(prs, output_file)
    print(f"CSV saved to {output_file}")


if __name__ == "__main__":
    main()
