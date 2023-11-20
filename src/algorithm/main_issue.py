import argparse
import json
from datetime import datetime
import git
import re


# %%
def get_diff(repo_path, commit_A, commit_B):
    repo = git.Repo(repo_path)
    diff = repo.git.diff(commit_A.hexsha, commit_B.hexsha, '-U0', '--histogram')
    return diff


def get_bug_fix_commits(repo):
    commits = repo.iter_commits()
    # retrieve bug fix commit
    bug_fix_commits = []
    for commit in commits:
        commit_message = commit.message.lower()
        match = is_fix_contained(commit_message)
        if match:
            bug_fix_commits.append(commit)
    return bug_fix_commits


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


def match_comment(line):
    comment_pattern = re.compile(r'^\s*(#|//|<!--|/\*)|(?:.*?--!>|.*?\*/)\s*$')

    return comment_pattern.match(line[1:])  # Ignora il primo carattere perchè le linee iniziano per '-'


# Funzione per ottenere i numeri delle issue
def is_fix_contained(issue_body):
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
        blame_result = repo.git.blame(parent_commit.hexsha, file_path, "--line-porcelain")
        candidate_commits = get_candidate_commits(blame_result, file_path, changes_dict)
        all_candidate_commits = all_candidate_commits.union(candidate_commits)

    return all_candidate_commits


def print_candidate_commit(total_candidate_commits):
    for element, value in total_candidate_commits.items():
        print('\nCommit ', element)
        print('Commit candidati')
        for com in value:
            print(com)


def szz(path_to_repo):
    repo = git.Repo(path_to_repo)
    commits = repo.iter_commits()
    # retrieve bug fix commit
    bug_fix_commits = []
    for commit in commits:
        commit_message = commit.message.lower()
        if 'bug' in commit_message and ('fix' or 'fixed') in commit_message:
            bug_fix_commits.append(commit)

    total_candidate_commit = {}
    # iteriamo su tutti i commit bug_fix
    for bug_fix_commit in bug_fix_commits[0:5]:
        # verifichiamo se il commit ha effettivamente un parent da confrontare, altrimenti non possiamo fare il
        # confronto
        if bug_fix_commit.parents is not None:
            # se non è nullo facciamo il diff
            parent_commit = bug_fix_commit.parents[0];
            diff = get_diff(path_to_repo, bug_fix_commit, parent_commit)

            # generiamo il dizionario che contiene come chiave i file cambiati e come valore i numeri di riga
            # modificati, ed in particolare le linee che dal commit parent sono state eliminate e sostituite col fix
            # del bug
            changes_dict = generate_changes_dict(diff)
            # una volta fatto ciò la funzione all_candidate_commits trova i commit che hanno modificato quelle linee
            # l'ultima volta
            all_candidate_commits = get_all_candidate_commits(repo, parent_commit, changes_dict)
            total_candidate_commit[bug_fix_commit] = all_candidate_commits

    print_candidate_commit(total_candidate_commit)


def szz_issue(path_to_repo, issue_data):
    suspect_commit_dict = {}
    repo = git.Repo(path_to_repo)

    bug_fix_commits = get_bug_fix_commits(repo)
    # supponiamo che le pull request contenute nel file siano già "closed"
    for bug_fix_commit in bug_fix_commits:

        pattern = re.compile(r'#(\d+)')
        match = pattern.search(bug_fix_commit.message)
        issue_number_in_bug_fix = int(match.group(1))
        # supponiamo che l'sha del commit bug_fix sia l'ultimo della pull request, quello che ne indica la chiusura
        commit_sha_bug_fix = bug_fix_commit.hexsha
        issue_opened_at = None
        print(f'The bug fix commit: {commit_sha_bug_fix} refers to issue {issue_number_in_bug_fix}')
        found = False
        for issue in issue_data:
            # numero dell'issue nel file delle issue
            issue_n = int(issue["number"])
            # se il numero dell'issue della pull request matcha con una contenuta nel file allora prendi la data
            # di creazione dell'issue
            if issue_n == issue_number_in_bug_fix:
                found = True
                print(f"The issue {issue_number_in_bug_fix} is present in the issue file, so it is possible to search "
                      f"for commits")
                issue_opened_at = issue['created_at']

                # andiamo a prendere il commit bug_fix avendo l'sha e il primo parent commit
                parent_commit = bug_fix_commit.parents[0]

                # facciamo il diff tra i due per ottenere le linee di codice cambiate
                diff = get_diff(path_to_repo, bug_fix_commit, parent_commit)
                changes_dic = generate_changes_dict(diff)

                # effettuiamo blame su tutte le modifiche per ottenere i commit che hanno introdotto le linee
                # modificate
                all_candidate_commits = get_all_candidate_commits(repo, parent_commit, changes_dic)
                suspect_commit = []

                # Itera su ciascun commit candidato ad essere commit che ha introdotto il bug ottenuto dal blame
                for commit_sha, author in all_candidate_commits:
                    # per ogni commit candidato, estraiamo la data
                    commit_bug = repo.commit(commit_sha)
                    # Ottieni la data del commit come timestamp
                    commit_date_timestamp = commit_bug.committed_date

                    # Converti la stringa ISO 8601 in un oggetto datetime
                    issue_opened_at_datetime = datetime.fromisoformat(issue_opened_at.replace('Z', '+00:00'))

                    # Estrai il timestamp Unix
                    timestamp_issue_opened_at = int(issue_opened_at_datetime.timestamp())

                    # Stampa solo i commit effettuati prima della data di apertura dell'issue
                    # cioè che sicuramente non sono fix parziali
                    if commit_date_timestamp < timestamp_issue_opened_at:
                        suspect_commit.append((commit_sha, commit_bug.author.name))
                suspect_commit_dict[commit_sha_bug_fix] = suspect_commit
        if not found:
            print(
                f'The bug_fix_commit: {commit_sha_bug_fix} contains a reference to issue {issue_number_in_bug_fix} but'
                f'is not contained in the file that has been passed')

    print('\n\n\nThis is the list of every bug fix commits and the relative bug inducing commits')
    print(suspect_commit_dict)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Insert repository name""")
    parser.add_argument('--repo-path', type=str, help="The absolute path to a local copy of the git repository from "
                                                      "where the git log is taken.")

    # Aggiungi l'opzione -i e specifica il parametro --issue
    parser.add_argument('-i', '--issue', type=str, help="The absolute path to a local copy of a JSON file containing "
                                                        "the issue bug report of the repository")

    args = parser.parse_args()
    path_to_repo = args.repo_path

    if args.issue:
        # Se -i è presente, richiama la funzione szz_issue con il parametro --issue
        try:
            with open(args.issue) as issue_path_file:
                issue_data = json.load(issue_path_file)
            szz_issue(path_to_repo, issue_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON content: {e}")
    else:
        # Altrimenti, richiama la funzione alternativa senza il parametro --issue
        szz(path_to_repo)
