import git
import re


# git diff between two commit
def get_diff(repo_path, commit_A, commit_B):
    repo = git.Repo(repo_path)
    diff = repo.git.diff(commit_A, commit_B, '-U0', '--histogram')
    return diff


# get the dictionary where the key is the file path and the value is a list of numbers of the changed lines
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


def get_candidate_commits(blame_result, file_path, changes_dict):
    # Definisci il pattern delle espressioni regolari
    pattern = re.compile(r'([a-f0-9]+)\s+(\d+)\s+(\d+)?(?:\s+(\d+))?\nauthor\s+([^\n]+)')

    # Inizializza il set di commit
    commit_set = set()

    # Trova tutte le corrispondenze nel testo di output
    matches = pattern.findall(blame_result)

    # Estrai le informazioni desiderate
    for match in matches:
        commit_hash, first_number, second_number, third_number, author = match

        # Controlla se il secondo numero è nella lista associata al percorso del file
        if int(second_number) in changes_dict.get(file_path, []):
            # Aggiungi le informazioni richieste al set
            commit_set.add((commit_hash, author))

    # Restituisci il set di commit
    return commit_set


def get_all_candidate_commits(repo, parent_commit, changes_dict):
    all_candidate_commits = set()

    for file_path, line_numbers in changes_dict.items():
        blame_result = repo.git.blame(parent_commit, file_path, "--line-porcelain")
        candidate_commits = get_candidate_commits(blame_result, file_path, changes_dict)
        all_candidate_commits = all_candidate_commits.union(candidate_commits)

    return all_candidate_commits

def print_candidate_commit(result):
    for element, value in total_candidate_commit.items():
        print('\nCommit ', element)
        print('Commit candidati')
        for com in value:
            print(com)


repo_name = "/Users/guido/Documents/Progetto/tensorflow"
repo = git.Repo(repo_name)
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
    # verifichiamo se il commit ha effettivamente un parent da confrontare, altrimenti non possiamo fare il confronto
    if bug_fix_commit.parents is not None:
        # se non è nullo facciamo il diff
        parent_commit = bug_fix_commit.parents[0];
        diff = get_diff(repo_name, bug_fix_commit, parent_commit)

        # generiamo il dizionario che contiene come chiave i file cambiati e come valore i numeri di riga modificati,
        # ed in particolare le linee che dal commit parent sono state eliminate e sostituite col fix del bug
        changes_dict = generate_changes_dict(diff)
        # una volta fatto ciò la funzione all_candidate_commits trova i commit che hanno modificato quelle linee
        # l'ultima volta
        all_candidate_commits = get_all_candidate_commits(repo, parent_commit, changes_dict)
        total_candidate_commit[bug_fix_commit] = all_candidate_commits

print_candidate_commit(total_candidate_commit)
