import argparse
import json
from datetime import datetime
import git
import re


def load_regex_config(config_path='../../regex_config.txt'):
    # Apre il file specificato e restituisce il contenuto come stringa, rimuovendo spazi bianchi in eccesso.
    try:
        with open(config_path, 'r') as config_file:
            return config_file.read().strip()
    except FileNotFoundError as e:
        # Stampa un messaggio di errore nel caso in cui il file non venga trovato.
        print(f"Error loading regex config: {e}")
        return None  # Ritorna None in caso di errore


def get_bug_fix_commits_szz_issue():
    commits = repo.iter_commits()
    bug_fix_commits = []
    for commit in commits:
        commit_message = commit.message.lower()
        match = is_fix_contained(commit_message, issue_pattern)
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

            # Aggiungi le linee modificate solo se non sono commenti
            if not match_comment(line):
                numbers_list.extend(range(start_line, start_line + num_lines))

    if current_file_path and numbers_list:
        result_dict[current_file_path] = numbers_list

    return result_dict


def match_comment(line):
    comment_pattern = re.compile(r'^\s*(#|//|<!--|/\*)|(?:.*?--!>|.*?\*/)\s*$')

    return comment_pattern.match(line[1:])  # Ignora il primo carattere perchè le linee iniziano per '-'


# Funzione per ottenere i numeri delle issue
def is_fix_contained(commit_message, issue_pattern):
    if not isinstance(commit_message, str):
        return False

    match = issue_pattern.search(commit_message)
    return bool(match)


def get_candidate_commits(blame_result, file_path, changes_dict):
    pattern = re.compile(r'([a-f0-9]+)\s+(\d+)\s+(\d+)?(?:\s+(\d+))?\nauthor\s+([^\n]+)')

    commit_set = set()
    most_recent_commit = None
    matches = pattern.findall(blame_result)

    for match in matches:
        commit_hash, first_number, second_number, third_number, author = match
        # se il numero di linea cambiato è presente nell'output del blame allora aggiungilo
        if int(second_number) in changes_dict.get(file_path, []):
            # in particolare, se la flag -r è specificata, aggiungi solo il commit più recente per il file
            if args.recent:
                # se nessun commit è stato indicato come più recente, o quello attuale è più recente di quello
                # precendente, allora aggiorna il commit più recente
                if most_recent_commit is None or commit_is_more_recent(commit_hash, most_recent_commit[0]):
                    most_recent_commit = (commit_hash, author)
            else:
                commit_set.add((commit_hash, author))

    # se è stata specificata la flag, allora l'unico commit da aggiungere è il più recente
    if args.recent and most_recent_commit is not None:
        commit_set.add(most_recent_commit)

    return commit_set


def commit_is_more_recent(commit_hash1, commit_hash2):
    commit1 = repo.commit(commit_hash1)
    commit2 = repo.commit(commit_hash2)
    return commit1.committed_date > commit2.committed_date


def get_all_candidate_commits(parent_commit, changes_dict):
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


def get_bug_fix_commits_for_szz():
    commits = repo.iter_commits()
    bug_fix_commits = []
    for commit in commits:
        commit_message = commit.message.lower()
        if 'bug' in commit_message and ('fix' in commit_message or 'fixed' in commit_message):
            bug_fix_commits.append(commit)

    return bug_fix_commits


def search_candidate_commit_szz(bug_fix_commit):
    all_candidate_commits = []
    # verifichiamo se il commit ha effettivamente un parent da confrontare, altrimenti non possiamo fare il
    # confronto
    if bug_fix_commit.parents is not None:
        parent_commit = bug_fix_commit.parents[0]
        diff = repo.git.diff(bug_fix_commit.hexsha, parent_commit.hexsha, '-U0', '--histogram')

        # generiamo il dizionario che contiene come chiave i file cambiati e come valore i numeri di riga
        # modificati, ed in particolare le linee che dal commit parent sono state eliminate e sostituite col fix
        # del bug
        changes_dict = generate_changes_dict(diff)
        # una volta fatto ciò la funzione all_candidate_commits trova i commit che hanno modificato quelle linee
        # l'ultima volta
        all_candidate_commits = get_all_candidate_commits(parent_commit, changes_dict)

    return all_candidate_commits


def extract_issue_number(commit_message, regex_pattern):
    # Utilizza il pattern di espressione regolare per cercare il numero dell'issue nel messaggio del commit.
    pattern = re.compile(regex_pattern)
    match = pattern.search(commit_message)
    if match:
        return int(match.group(1))
    return None


def extract_commit_by_timestamp(all_candidate_commits, issue_opened_at):
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

    return suspect_commit


def szz():
    bug_fix_commits = get_bug_fix_commits_for_szz()

    total_candidate_commit = {}
    # iteriamo su tutti i commit bug_fix
    for bug_fix_commit in bug_fix_commits[0:5]:
        # chiamiamo la funzione che fa diff, blame e ottiene i commit candidati
        total_candidate_commit[bug_fix_commit] = search_candidate_commit_szz(bug_fix_commit)

    print_candidate_commit(total_candidate_commit)


def szz_issue():
    suspect_commit_dict = {}

    bug_fix_commits = get_bug_fix_commits_szz_issue()
    for bug_fix_commit in bug_fix_commits:
        issue_number_in_bug_fix = extract_issue_number(bug_fix_commit.message, issue_pattern)
        commit_sha_bug_fix = bug_fix_commit.hexsha

        print(f'The bug fix commit: {commit_sha_bug_fix} refers to issue {issue_number_in_bug_fix}')
        found = False

        for issue in issue_data:
            issue_n = int(issue["number"])

            if issue_n == issue_number_in_bug_fix:
                found = True
                print(f"The issue {issue_number_in_bug_fix} is present in the issue file, so it is possible to search "
                      f"for commits")
                issue_opened_at = issue['created_at']
                all_candidate_commits = search_candidate_commit_szz(bug_fix_commit)
                suspect_commit_dict[commit_sha_bug_fix] = extract_commit_by_timestamp(all_candidate_commits,
                                                                                      issue_opened_at)
        if not found:
            print(f'The bug_fix_commit: {commit_sha_bug_fix} contains a reference to issue {issue_number_in_bug_fix} '
                  f'but is not contained in the file that has been passed')

    print('\n\n\nThis is the list of every bug fix commits and the relative bug inducing commits')
    print_candidate_commit(suspect_commit_dict)


args = None
repo = None
issue_pattern = None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Insert repository name""")
    parser.add_argument('--repo-path', type=str, help="The absolute path to a local copy of the git repository from "
                                                      "where the git log is taken.")

    # Aggiungi l'opzione -i e specifica il parametro --issue
    parser.add_argument('-i', '--issue', type=str, help="The absolute path to a local copy of a JSON file containing "
                                                        "the issue bug report of the repository")

    # Aggiungi l'opzione -r e specifica il parametro --recent
    parser.add_argument('-r', '--recent', action='store_true',
                        help="Show only the most recent commit for each bug-fix commit")

    args = parser.parse_args()
    path_to_repo = args.repo_path
    repo = git.Repo(path_to_repo)
    issue_pattern_str = load_regex_config()

    if issue_pattern_str is not None:
        issue_pattern = re.compile(issue_pattern_str)

        if args.issue:
            try:
                with open(args.issue) as issue_path_file:
                    issue_data = json.load(issue_path_file)
                szz_issue()
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON content: {e}")
        else:
            szz()
    else:
        print("No valid issue pattern found. Please check the regex_config.txt file.")
