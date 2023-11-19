import argparse
import json
from datetime import datetime
import git
import re


# %%
def get_diff(repo_path, commit_A, commit_B):
    repo = git.Repo(repo_path)
    diff = repo.git.diff(commit_A.sha, commit_B.sha, '-U0', '--histogram')
    return diff


def generate_changes_dict(diff_output):
    file_path_pattern = re.compile(r'^\+\+\+ b/(.*)$')
    line_number_pattern = re.compile(r'^@@ -(\d+)(,(\d+))? \+(\d+)(,(\d+))? @@')

    result_dict = {}
    current_file_path = None
    numbers_list = []

    diff_lines = diff_output.split('\n')

    for line in diff_lines:
        file_path_match = file_path_pattern.match(line)
        line_number_match = line_number_pattern.match(line)

        if file_path_match:
            if current_file_path and numbers_list:
                result_dict[current_file_path] = numbers_list
                numbers_list = []

            current_file_path = file_path_match.group(1)
        elif line_number_match:
            start_line = int(line_number_match.group(1))
            num_lines = 1 if line_number_match.group(3) is None else int(line_number_match.group(3))

            numbers_list.extend(range(start_line, start_line + num_lines))

    if current_file_path and numbers_list:
        result_dict[current_file_path] = numbers_list

    return result_dict


# Funzione per ottenere i numeri delle issue
def get_issue_numbers(issue_body):
    if not isinstance(issue_body, str):
        return None

    pattern = re.compile(r'#(\d+)')
    match = pattern.search(issue_body)
    return match


def get_candidate_commits(blame_result, file_path, changes_dict):
    pattern = re.compile(r'([a-f0-9]+)\s+(\d+)\s+(\d+)?(?:\s+(\d+))?\nauthor\s+([^\n]+)')

    commit_set = set()

    matches = pattern.findall(blame_result)

    for match in matches:
        commit_hash, first_number, second_number, third_number, author = match

        if int(second_number) in changes_dict.get(file_path, []):
            commit_set.add((commit_hash, author))

    return commit_set


def get_all_candidate_commits(repo, parent_commit, changes_dict):
    all_candidate_commits = set()

    for file_path, line_numbers in changes_dict.items():
        blame_result = repo.git.blame(parent_commit.sha, file_path, "--line-porcelain")
        candidate_commits = get_candidate_commits(blame_result, file_path, changes_dict)
        all_candidate_commits = all_candidate_commits.union(candidate_commits)

    return all_candidate_commits


def szz(path_to_repo, pull_request_data, issue_data):
    suspect_commit_dict = {}
    suspect_commit = []
    repo = git.Repo(path_to_repo)
    # supponiamo che le pull request contenute nel file siano già "closed"
    for pull_request in pull_request_data:

        # supponiamo che l'sha del commit bug_fix sia l'ultimo della pull request, quello che ne indica la chiusura
        commit_sha_bug_fix = pull_request['head']
        issue_opened_at = None
        # iteriamo su tutte le pull request del file e per ognuna cerchiamo la issue associata con una regex
        match = get_issue_numbers(pull_request['body'])

        if match is not None:
            # se troviamo l'espressione regolare che indica il riferimento dell'issue alla pull request allora la
            # assegnamo alla variabile issue number
            issue_number = int(match.group(1))

            for issue in issue_data:
                # numero dell'issue nel file delle issue
                issue_n = int(issue["number"])
                # se il numero dell'issue della pull request matcha con una contenuta nel file allora prendi la data
                # di creazione dell'issue
                if issue_n == issue_number:
                    print("Issue found!")
                    issue_opened_at = issue['created_at']

                    # andiamo a prendere il commit bug_fix avendo l'sha e il primo parent commit
                    commit_bug_fix = repo.commit(commit_sha_bug_fix)
                    parent_commit = commit_bug_fix.parents[0]

                    # facciamo il diff tra i due per ottenere le linee di codice cambiate
                    diff = get_diff(path_to_repo, commit_bug_fix, parent_commit)
                    changes_dic = generate_changes_dict(diff)

                    # effettuiamo blame su tutte le modifiche per ottenere i commit che hanno introdotto le linee
                    # modificate
                    all_candidate_commits = get_all_candidate_commits(repo, parent_commit, changes_dic)

                    # Itera su ciascun commit candidato ad essere commit che ha introdotto il bug ottenuto dal blame
                    for commit_sha, author in all_candidate_commits:
                        # per ogni commit candidato, estraiamo la data
                        commit = repo.commit(commit_sha)
                        # Ottieni la data del commit come timestamp
                        commit_date_timestamp = commit.committed_date

                        # Converti la stringa ISO 8601 in un oggetto datetime
                        issue_opened_at_datetime = datetime.fromisoformat(issue_opened_at.replace('Z', '+00:00'))

                        # Estrai il timestamp Unix
                        timestamp_issue_opened_at = int(issue_opened_at_datetime.timestamp())

                        # Stampa solo i commit effettuati prima della data di apertura dell'issue
                        # cioè che sicuramente non sono fix parziali
                        if commit_date_timestamp < timestamp_issue_opened_at:
                            suspect_commit_dict[commit_sha_bug_fix] = suspect_commit.append(commit_sha)
        else:
            print("Issue not found")

    print(suspect_commit_dict)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="""Insert repository name
                                                 """)
    parser.add_argument('--repo-path', type=str,
                        help="The absolute path to a local copy of the git repository from where the git log is taken.")

    parser.add_argument('--pull-request', type=str,
                        help="The absolute path to a local copy of a JSON file containing the pull request of the "
                             "repository")

    parser.add_argument('--issue', type=str,
                        help="The absolute path to a local copy of a JSON file containing the issue bug report of the "
                             "repository")

    args = parser.parse_args()
    path_to_repo = args.repo_path
    pull_request_path = args.pull_request
    issue_path = args.issue

    try:
        with open(pull_request_path) as pull_request_path_file:
            pull_request_data = json.load(pull_request_path_file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON content: {e}")
        pull_request_data = None

    try:
        with open(issue_path) as issue_path_file:
            issue_data = json.load(issue_path_file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON content: {e}")
        issue_data = None

    szz(path_to_repo, pull_request_data, issue_data)
