import unittest
from unittest.mock import MagicMock, patch, call, mock_open
import re

from src.main import get_bug_fix_commits_for_szz, generate_changes_dict, get_candidate_commits, \
    get_all_candidate_commits, extract_issue_number, match_comment, is_fix_contained, \
    get_bug_fix_commits_szz_issue, \
    search_candidate_commit_szz, \
    print_candidate_commit, szz, \
    load_regex_config, commit_is_more_recent, szz_issue, extract_commit_by_timestamp  # Assicurati di sostituire 'your_script' con il nome reale del tuo script


class UnitTest(unittest.TestCase):

    @patch('src.main.repo', autospec=True)
    def test_get_bug_fix_commits_for_szz_with_bug_and_fix(self, mock_repo):
        # Crea alcuni commit mock con messaggi specifici per il testing
        mock_commits = [
            MagicMock(message="Fixing a bug"),
            MagicMock(message="Adding a new feature"),
            MagicMock(message="Fix: Another bug in the code")
        ]

        # Imposta la proprietà iter_commits del mock_repo
        mock_repo.iter_commits.return_value = mock_commits

        # Esegui la funzione di test
        bug_fix_commits = get_bug_fix_commits_for_szz()

        # Verifica che la funzione restituisca i commit corretti
        self.assertEqual(bug_fix_commits, [mock_commits[0], mock_commits[2]])

    @patch('src.main.repo', autospec=True)
    def test_get_bug_fix_commits_for_szz_with_bug_and_fixed(self, mock_repo):
        # Crea alcuni commit mock con messaggi specifici per il testing
        mock_commits = [
            MagicMock(message="Fixed a bug"),
            MagicMock(message="Adding a new feature"),
            MagicMock(message="Bug fix: Another bug in the code")
        ]

        # Imposta la proprietà iter_commits del mock_repo
        mock_repo.iter_commits.return_value = mock_commits

        # Esegui la funzione di test
        bug_fix_commits = get_bug_fix_commits_for_szz()

        # Verifica che la funzione restituisca i commit corretti
        self.assertEqual(bug_fix_commits, [mock_commits[0], mock_commits[2]])

    @patch('src.main.repo', autospec=True)
    def test_get_bug_fix_commits_for_szz_with_fix_only(self, mock_repo):
        # Crea alcuni commit mock con messaggi specifici per il testing
        mock_commits = [
            MagicMock(message="Fix #123456"),
            MagicMock(message="Fixing another issue"),
            MagicMock(message="Fix: Another problem in the code")
        ]

        # Imposta la proprietà iter_commits del mock_repo
        mock_repo.iter_commits.return_value = mock_commits

        # Esegui la funzione di test
        bug_fix_commits = get_bug_fix_commits_for_szz()

        # Verifica che la funzione restituisca una lista vuota
        self.assertEqual(bug_fix_commits, [])

    @patch('src.main.repo', autospec=True)
    def test_get_bug_fix_commits_for_szz_with_bug_only(self, mock_repo):
        # Crea alcuni commit mock con messaggi specifici per il testing
        mock_commits = [
            MagicMock(message="Bug #123456"),
            MagicMock(message="Fixing another issue"),
            MagicMock(message="Bug: Another problem in the code")
        ]

        # Imposta la proprietà iter_commits del mock_repo
        mock_repo.iter_commits.return_value = mock_commits

        # Esegui la funzione di test
        bug_fix_commits = get_bug_fix_commits_for_szz()

        # Verifica che la funzione restituisca una lista vuota
        self.assertEqual(bug_fix_commits, [])

    @patch('src.main.repo', autospec=True)
    def test_get_bug_fix_commits_for_szz_with_empty_message(self, mock_repo):
        # Crea alcuni commit mock con messaggi specifici per il testing
        mock_commits = [
            MagicMock(message=""),
            MagicMock(message=""),
            MagicMock(message="")
        ]

        # Imposta la proprietà iter_commits del mock_repo
        mock_repo.iter_commits.return_value = mock_commits

        # Esegui la funzione di test
        bug_fix_commits = get_bug_fix_commits_for_szz()

        # Verifica che la funzione restituisca una lista vuota
        self.assertEqual(bug_fix_commits, [])

    @patch('src.main.is_fix_contained', autospec=True)
    @patch('src.main.repo', autospec=True)
    def test_get_bug_fix_commits_szz_issue_true(self, mock_repo, mock_is_fix_contained):
        # Configura il mock del repository
        mock_commits = [
            MagicMock(message="Fixing a bug"),
            MagicMock(message="Adding a new feature"),
            MagicMock(message="Fix: Another bug in the code")
        ]
        mock_repo.iter_commits.return_value = mock_commits
        mock_is_fix_contained.return_value = True
        # Chiamata alla funzione da testare
        result = get_bug_fix_commits_szz_issue()

        # Verifica che il risultato sia una lista di commit che contengono correzioni di bug
        self.assertEqual(result, [mock_commits[0], mock_commits[1], mock_commits[2]])

    @patch('src.main.is_fix_contained', autospec=True)
    @patch('src.main.repo', autospec=True)
    def test_get_bug_fix_commits_szz_issue_false(self, mock_repo, mock_is_fix_contained):
        # Configura il mock del repository
        mock_commits = [
            MagicMock(message="Fixing a bug"),
            MagicMock(message="Adding a new feature"),
            MagicMock(message="Fix: Another bug in the code")
        ]
        mock_repo.iter_commits.return_value = mock_commits
        mock_is_fix_contained.return_value = False
        # Chiamata alla funzione da testare
        result = get_bug_fix_commits_szz_issue()

        # Verifica che il risultato sia una lista di commit che contengono correzioni di bug
        self.assertEqual(result, [])

    @patch('builtins.open', mock_open(read_data='regex'))
    def test_load_regex_config_success(self):
        result = load_regex_config('fake_path')
        self.assertEqual(result, 'regex')

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_regex_config_file_not_found(self, mock_open_file):
        result = load_regex_config('nonexistent_path')
        self.assertIsNone(result)

    def test_generate_changes_dict_diff_output_not_empty(self):
        # Esempio di output del diff
        diff_output = """ diff --git a/third_party/xla/xla/service/gpu/BUILD b/third_party/xla/xla/service/gpu/BUILD
index 67468fef9b5..00f1d5ebe98 100644
--- a/third_party/xla/xla/service/gpu/BUILD
+++ b/third_party/xla/xla/service/gpu/BUILD
@@ -3469 +3468,0 @@ cc_library(
-        "@com_google_absl//absl/algorithm:container",
@@ -3471 +3469,0 @@ cc_library(
-        "@com_google_absl//absl/log:check" """
        # Esempio di output atteso dal tuo codice
        expected_output = {
            'third_party/xla/xla/service/gpu/BUILD': [3469, 3471]
        }

        # Esegui la funzione e verifica se l'output è corretto
        changes_dict = generate_changes_dict(diff_output)
        self.assertEqual(changes_dict, expected_output)

    def test_generate_changes_dict_diff_output_empty(self):
        # Esempio di output del diff
        diff_output = ""
        # Esempio di output atteso dal tuo codice
        expected_output = {}

        # Esegui la funzione e verifica se l'output è corretto
        changes_dict = generate_changes_dict(diff_output)
        self.assertEqual(changes_dict, expected_output)

    @patch('src.main.args', recent=False)
    def test_get_candidate_commits_with_changes_no_recent_flag(self, mock_args):
        blame_result = """
        f4529e80ab30a51207901b74b438980ac8b3ceaf 1 1 23
author Adrian Kuegel
author-mail <akuegel@google.com>
author-time 1695130818
author-tz -0700
committer TensorFlower Gardener
committer-mail <gardener@tensorflow.org>
committer-time 1695131394
committer-tz -0700
summary [XLA:GPU] Move buffer sharing logic into a separate target (NFC).
filename third_party/xla/xla/service/gpu/buffer_sharing.cc
	/* Copyright 2023 The TensorFlow Authors. All Rights Reserved.
	85ac1c6ddc93d4f53ff5b2c5c1c7bac7a8a44030 35 35
author Sergey Kozub
author-mail <sergeykozub@google.com>
author-time 1698139134
author-tz -0700
committer TensorFlower Gardener
committer-mail <gardener@tensorflow.org>
committer-time 1698139458
committer-tz -0700
summary Allow reduction users in multi-output fusions with buffer aliasing (FusionCanShareBufferHint)
previous 2cf8b1c62a98c859bbe2ae69160680eea6aae160 
third_party/xla/xla/service/gpu/buffer_sharing.cc
filename third_party/xla/xla/service/gpu/buffer_sharing.cc
	#include "xla/stream_executor/device_description.pb.h"
        """
        file_path = 'third_party/xla/xla/service/gpu/buffer_sharing.cc'
        changes_dict = {'third_party/xla/xla/service/gpu/buffer_sharing.cc': [1, 35]}

        expected_commits = {('85ac1c6ddc93d4f53ff5b2c5c1c7bac7a8a44030', 'Sergey Kozub'),
                            ("f4529e80ab30a51207901b74b438980ac8b3ceaf", "Adrian Kuegel"), }

        commit_set = get_candidate_commits(blame_result, file_path, changes_dict)
        self.assertEqual(commit_set, expected_commits)

    # il mock con side_effect=lambda x, y: True semplifica
    # il confronto facendo sì che restituisca sempre True, ovvero indicando che il primo commit è sempre meno recente del secondo.
    @patch('src.main.commit_is_more_recent', side_effect=lambda x, y: True)
    def test_get_candidate_commits_with_changes_and_recent_flag(self, mock_commit_is_more_recent):
        blame_result = """
        f4529e80ab30a51207901b74b438980ac8b3ceaf 1 1 23
author Adrian Kuegel
author-mail <akuegel@google.com>
author-time 1695130818
author-tz -0700
committer TensorFlower Gardener
committer-mail <gardener@tensorflow.org>
committer-time 1695131394
committer-tz -0700
summary [XLA:GPU] Move buffer sharing logic into a separate target (NFC).
filename third_party/xla/xla/service/gpu/buffer_sharing.cc
	/* Copyright 2023 The TensorFlow Authors. All Rights Reserved.
        85ac1c6ddc93d4f53ff5b2c5c1c7bac7a8a44030 35 35
author Sergey Kozub
author-mail <sergeykozub@google.com>
author-time 1698139134
author-tz -0700
committer TensorFlower Gardener
committer-mail <gardener@tensorflow.org>
committer-time 1698139458
committer-tz -0700
summary Allow reduction users in multi-output fusions with buffer aliasing (FusionCanShareBufferHint)
previous 2cf8b1c62a98c859bbe2ae69160680eea6aae160 
third_party/xla/xla/service/gpu/buffer_sharing.cc
filename third_party/xla/xla/service/gpu/buffer_sharing.cc
	#include "xla/stream_executor/device_description.pb.h"
        """
        file_path = 'third_party/xla/xla/service/gpu/buffer_sharing.cc'
        changes_dict = {'third_party/xla/xla/service/gpu/buffer_sharing.cc': [1, 35]}

        # Imposta args.recent a True (come se fosse passato il flag -r)
        with patch('src.main.args', recent=True):
            result = get_candidate_commits(blame_result, file_path, changes_dict)

        expected_result = {('85ac1c6ddc93d4f53ff5b2c5c1c7bac7a8a44030', 'Sergey Kozub')}

        self.assertEqual(result, expected_result)

    @patch('src.main.args', recent=False or True)
    def test_get_candidate_commits_no_changes(self, mock_args):
        blame_result = ""
        file_path = 'some/file/path'
        changes_dict = {'some/file/path': [2, 5]}

        expected_commits = set()

        commit_set = get_candidate_commits(blame_result, file_path, changes_dict)
        self.assertEqual(commit_set, expected_commits)

    @patch('src.main.args', recent=False or True)
    def test_get_candidate_commits_line_not_in_changes_dict(self, mock_args):
        blame_result = """
        f4529e80ab30a51207901b74b438980ac8b3ceaf 1 1 23
author Adrian Kuegel
author-mail <akuegel@google.com>
author-time 1695130818
author-tz -0700
committer TensorFlower Gardener
committer-mail <gardener@tensorflow.org>
committer-time 1695131394
committer-tz -0700
summary [XLA:GPU] Move buffer sharing logic into a separate target (NFC).
filename third_party/xla/xla/service/gpu/buffer_sharing.cc
	/* Copyright 2023 The TensorFlow Authors. All Rights Reserved.
        85ac1c6ddc93d4f53ff5b2c5c1c7bac7a8a44030 35 35
author Sergey Kozub
author-mail <sergeykozub@google.com>
author-time 1698139134
author-tz -0700
committer TensorFlower Gardener
committer-mail <gardener@tensorflow.org>
committer-time 1698139458
committer-tz -0700
summary Allow reduction users in multi-output fusions with buffer aliasing (FusionCanShareBufferHint)
previous 2cf8b1c62a98c859bbe2ae69160680eea6aae160 
third_party/xla/xla/service/gpu/buffer_sharing.cc
filename third_party/xla/xla/service/gpu/buffer_sharing.cc
	#include "xla/stream_executor/device_description.pb.h"
        """
        file_path = 'third_party/xla/xla/service/gpu/buffer_sharing.cc'
        changes_dict = {'third_party/xla/xla/service/gpu/buffer_sharing.cc': [5, 8]}

        expected_commits = set()

        commit_set = get_candidate_commits(blame_result, file_path, changes_dict)
        self.assertEqual(commit_set, expected_commits)

    @patch('src.main.args', recent=False or True)
    def test_get_candidate_commits_partial_changes(self, mock_args):
        blame_result = """
        f4529e80ab30a51207901b74b438980ac8b3ceaf 1 1 23
author Adrian Kuegel
author-mail <akuegel@google.com>
author-time 1695130818
author-tz -0700
committer TensorFlower Gardener
committer-mail <gardener@tensorflow.org>
committer-time 1695131394
committer-tz -0700
summary [XLA:GPU] Move buffer sharing logic into a separate target (NFC).
filename third_party/xla/xla/service/gpu/buffer_sharing.cc
	/* Copyright 2023 The TensorFlow Authors. All Rights Reserved.
        85ac1c6ddc93d4f53ff5b2c5c1c7bac7a8a44030 35 35
author Sergey Kozub
author-mail <sergeykozub@google.com>
author-time 1698139134
author-tz -0700
committer TensorFlower Gardener
committer-mail <gardener@tensorflow.org>
committer-time 1698139458
committer-tz -0700
summary Allow reduction users in multi-output fusions with buffer aliasing (FusionCanShareBufferHint)
previous 2cf8b1c62a98c859bbe2ae69160680eea6aae160 
third_party/xla/xla/service/gpu/buffer_sharing.cc
filename third_party/xla/xla/service/gpu/buffer_sharing.cc
	#include "xla/stream_executor/device_description.pb.h"
        """
        file_path = 'third_party/xla/xla/service/gpu/buffer_sharing.cc'
        changes_dict = {'third_party/xla/xla/service/gpu/buffer_sharing.cc': [35, 120]}

        expected_commits = {('85ac1c6ddc93d4f53ff5b2c5c1c7bac7a8a44030', 'Sergey Kozub')}

        commit_set = get_candidate_commits(blame_result, file_path, changes_dict)
        self.assertEqual(commit_set, expected_commits)

    @patch('src.main.repo', autospec=True)
    @patch('src.main.get_candidate_commits',
           side_effect=[
               {('commit1', 'author1')},  # Risultato per 'file1'
               {('commit2', 'author2')}  # Risultato per 'file2'
           ])
    def test_get_all_candidate_commits_scenario1(self, mock_get_candidate_commits, mock_repo):
        # in questo scenario la chiamata get_candidate_commit() ha restituito commit diversi per i due file
        parent_commit = MagicMock()
        changes_dict = {'file1': [1, 2], 'file2': [3, 4]}

        result = get_all_candidate_commits(parent_commit, changes_dict)

        expected_commits = {('commit1', 'author1'), ('commit2', 'author2')}
        self.assertEqual(result, expected_commits)

    @patch('src.main.repo', autospec=True)
    @patch('src.main.get_candidate_commits',
           side_effect=[
               {('commit1', 'author1')},  # Risultato per 'file1'
               {('commit1', 'author1')}  # Risultato per 'file2'
           ])
    def test_get_all_candidate_commits_scenario2(self, mock_get_candidate_commits, mock_repo):
        # in questo scenario la chiamata get_candidate_commit() ha restituito lo stesso commit per i due file
        parent_commit = MagicMock()
        changes_dict = {'file1': [1, 2], 'file2': [3, 4]}

        result = get_all_candidate_commits(parent_commit, changes_dict)

        expected_commits = {('commit1', 'author1')}
        self.assertEqual(result, expected_commits)

    @patch('src.main.repo', autospec=True)
    @patch('src.main.get_candidate_commits',
           side_effect=[
               {},  # Risultato per 'file1'
               {}  # Risultato per 'file2'
           ])
    def test_get_all_candidate_commits_scenario3(self, mock_get_candidate_commits, mock_repo):
        # in questo scenario la chiamata get_candidate_commit() non ha restituito commit per i due file
        parent_commit = MagicMock()
        changes_dict = {'file1': [1, 2], 'file2': [3, 4]}

        result = get_all_candidate_commits(parent_commit, changes_dict)

        expected_commits = set()
        self.assertEqual(result, expected_commits)

    @patch('src.main.repo', autospec=True)
    @patch('src.main.generate_changes_dict', autospec=True)
    @patch('src.main.get_all_candidate_commits', autospec=True)
    def test_search_candidate_commit_szz_with_parent_commit(self, mock_get_all_candidate_commits,
                                                            mock_generate_changes_dict, mock_repo):
        # Crea un mock per il bug_fix_commit
        bug_fix_commit = MagicMock()
        bug_fix_commit.parents = [MagicMock()]  # Assicurati che ci sia almeno un parent

        # Configura il comportamento desiderato per i mock
        mock_diff = MagicMock()
        mock_repo.git.diff.return_value = mock_diff
        mock_generate_changes_dict.return_value = {'file1': [1, 2, 3], 'file2': [4, 5]}
        mock_get_all_candidate_commits.return_value = {('commit1', 'author1'), ('commit2', 'author2')}

        # Esegui la funzione di test
        result = search_candidate_commit_szz(bug_fix_commit)

        # Verifica che la funzione restituisca i risultati attesi
        self.assertEqual(result, {('commit1', 'author1'), ('commit2', 'author2')})

        # Verifica le chiamate ai metodi
        mock_repo.git.diff.assert_called_with(bug_fix_commit.hexsha, bug_fix_commit.parents[0].hexsha, '-U0',
                                              '--histogram')
        mock_generate_changes_dict.assert_called_with(mock_diff)
        mock_get_all_candidate_commits.assert_called_with(bug_fix_commit.parents[0],
                                                          {'file1': [1, 2, 3], 'file2': [4, 5]})

    @patch('src.main.repo', autospec=True)
    @patch('src.main.generate_changes_dict', autospec=True)
    @patch('src.main.get_all_candidate_commits', autospec=True)
    def test_search_candidate_commit_szz_without_parent_commit(self, mock_get_all_candidate_commits,
                                                               mock_generate_changes_dict, mock_repo):
        bug_fix_commit = MagicMock()
        bug_fix_commit.parents = None  # Nessun parent commit

        # Esegui la funzione di test
        result = search_candidate_commit_szz(bug_fix_commit)

        # Verifica che la funzione restituisca una lista vuota senza chiamare altri metodi
        self.assertEqual(result, [])
        mock_repo.git.diff.assert_not_called()
        mock_generate_changes_dict.assert_not_called()
        mock_get_all_candidate_commits.assert_not_called()

    @patch('builtins.print')  # Mock la funzione print built-in
    def test_print_candidate_commit_not_empty(self, mock_print):
        # Configura dati di esempio
        mock_bug_fix_commit1 = MagicMock()
        mock_bug_fix_commit2 = MagicMock()
        mock_bug_fix_commit3 = MagicMock()

        total_candidate_commits = {
            mock_bug_fix_commit1: [('commit1', 'author1'), ('commit2', 'author2')],
            mock_bug_fix_commit2: [('commit3', 'author3'), ('commit4', 'author4')],
            mock_bug_fix_commit3: [('commit5', 'author5'), ('commit6', 'author6')],
        }

        # Esegui la funzione di test
        print_candidate_commit(total_candidate_commits)

        # Cattura l'output effettivo della funzione print
        captured_output = [call[0] for call in mock_print.call_args_list]

        # Output desiderato
        expected_output = [
            ('\nCommit ', mock_bug_fix_commit1),
            ('Commit candidati',),
            (('commit1', 'author1'),),
            (('commit2', 'author2'),),
            ('\nCommit ', mock_bug_fix_commit2),
            ('Commit candidati',),
            (('commit3', 'author3'),),
            (('commit4', 'author4'),),
            ('\nCommit ', mock_bug_fix_commit3),
            ('Commit candidati',),
            (('commit5', 'author5'),),
            (('commit6', 'author6'),),
        ]

        # Verifica che l'output effettivo sia uguale all'output desiderato
        self.assertEqual(captured_output, expected_output)

    @patch('builtins.print')  # Mock la funzione print built-in
    def test_print_candidate_commit_empty(self, mock_print):
        total_candidate_commits = {}

        # Esegui la funzione di test
        print_candidate_commit(total_candidate_commits)

        # Cattura l'output effettivo della funzione print
        captured_output = [call[0] for call in mock_print.call_args_list]

        # Output desiderato
        expected_output = []

        # Verifica che l'output effettivo sia uguale all'output desiderato
        self.assertEqual(captured_output, expected_output)

    @patch('src.main.get_bug_fix_commits_for_szz')
    @patch('src.main.search_candidate_commit_szz')
    @patch('src.main.print_candidate_commit')
    def test_szz_function(self, mock_print, mock_search, mock_get_bug_fix_commits):
        # Configurare il comportamento del mock per ogni funzione
        mock_get_bug_fix_commits.return_value = ['commit1', 'commit2', 'commit3', 'commit4', 'commit5']
        mock_search.return_value = 'mock_candidate_commit'

        szz()

        # Verifica che get_bug_fix_commits_for_szz venga chiamato una volta
        mock_get_bug_fix_commits.assert_called_once_with()

        # Verifica che search_candidate_commit_szz venga chiamato 5 volte con i primi 5 commit di bug_fix_commits
        expected_calls = [call('commit1'), call('commit2'), call('commit3'), call('commit4'), call('commit5')]
        mock_search.assert_has_calls(expected_calls)

        # Verifica che print_candidate_commit venga chiamato una volta
        mock_print.assert_called_once()

    @patch('src.main.repo')
    def test_commit_is_more_recent_false(self, mock_repo):
        # Configura dati di esempio
        mock_commit1 = MagicMock()
        mock_commit1.committed_date = 1637878400

        mock_commit2 = MagicMock()
        mock_commit2.committed_date = 1638260400

        # Configura il mock del repository
        mock_repo.commit.side_effect = [mock_commit1, mock_commit2]

        # Chiamata al metodo da testare
        result = commit_is_more_recent('hash1', 'hash2')

        # Verifica il risultato atteso
        self.assertFalse(result)  # Il commit1 è meno recente di commit2

    @patch('src.main.repo')
    def test_commit_is_more_recent_false_equal_timestamp(self, mock_repo):
        # Configura dati di esempio
        mock_commit1 = MagicMock()
        mock_commit1.committed_date = 1637878400

        mock_commit2 = MagicMock()
        mock_commit2.committed_date = 1637878400

        # Configura il mock del repository
        mock_repo.commit.side_effect = [mock_commit1, mock_commit2]

        # Chiamata al metodo da testare
        result = commit_is_more_recent('hash1', 'hash2')

        # Verifica il risultato atteso
        self.assertFalse(result)

    @patch('src.main.repo')
    def test_commit_is_more_recent_true(self, mock_repo):
        # Configura dati di esempio
        mock_commit1 = MagicMock()
        mock_commit1.committed_date = 1647878400

        mock_commit2 = MagicMock()
        mock_commit2.committed_date = 1638260400

        # Configura il mock del repository
        mock_repo.commit.side_effect = [mock_commit1, mock_commit2]

        # Chiamata al metodo da testare
        result = commit_is_more_recent('hash1', 'hash2')

        # Verifica il risultato atteso
        self.assertTrue(result)  # Il commit1 è più recente di commit2

    def test_extract_issue_number_found(self):
        result = extract_issue_number("Fixes issue #42", r'(\d+)')
        self.assertEqual(result, 42)

    def test_extract_issue_number_not_found(self):
        result = extract_issue_number("Fixes issue #", r'(\d+)')
        self.assertIsNone(result)

    def test_extract_issue_number_non_numeric(self):
        result = extract_issue_number("Fixes issue non_numeric", r'(\d+)')
        self.assertIsNone(result)

    def test_extract_issue_number_invalid_match(self):
        result = extract_issue_number("Fixes issue without a number", r'(\d+)')
        self.assertIsNone(result)

    def test_match_single_line_double_slash(self):
        line = " // This is a comment"
        result = match_comment(line)
        self.assertIsNotNone(result, "Expected a comment, but got None.")

    def test_match_multiline_single_quotes(self):
        line = " '''This is a multiline\ncomment'''"
        result = match_comment(line)
        self.assertIsNotNone(result, "Expected a comment, but got None.")

    def test_match_multiline_double_quotes(self):
        line = ' """This is another\nmultiline comment"""'
        result = match_comment(line)
        self.assertIsNotNone(result, "Expected a comment, but got None.")

    def test_match_comment_with_leading_spaces(self):
        line = "   # Comment with leading spaces"
        result = match_comment(line)
        self.assertIsNotNone(result, "Expected a comment, but got None.")

    def test_not_match_diff_output_line(self):
        line = "+ This is an added line from diff output"
        result = match_comment(line)
        self.assertIsNone(result, "Expected None for diff output line, but got a result.")

    def test_issue_pattern_found(self):
        commit_message = "Fixed issue #123"
        issue_pattern = re.compile(r'#(\d+)', re.IGNORECASE)
        result = is_fix_contained(commit_message, issue_pattern)
        self.assertTrue(result)

    def test_issue_pattern_not_found(self):
        commit_message = "This commit does not reference any issue."
        issue_pattern = re.compile(r'#(\d+)', re.IGNORECASE)
        result = is_fix_contained(commit_message, issue_pattern)
        self.assertFalse(result)

    def test_non_string_input(self):
        commit_message = None
        issue_pattern = re.compile(r'#(\d+)', re.IGNORECASE)
        result = is_fix_contained(commit_message, issue_pattern)
        self.assertFalse(result)

    def different_char_sensitive_matching(self):
        commit_message = "Fixed Issue -123"
        issue_pattern = re.compile(r'#(\d+)')
        result = is_fix_contained(commit_message, issue_pattern)
        self.assertFalse(result)

    def test_case_insensitive_matching(self):
        commit_message = "Fixed Issue #123"
        issue_pattern = re.compile(r'issue #(\d+)', re.IGNORECASE)
        result = is_fix_contained(commit_message, issue_pattern)
        self.assertTrue(result)

    def test_case_sensitive_matching(self):
        commit_message = "fixed issue #123"
        issue_pattern = re.compile(r'issue #(\d+)', re.IGNORECASE)
        result = is_fix_contained(commit_message, issue_pattern)
        self.assertTrue(result)

    @patch('src.main.repo')
    def test_extract_commit_by_timestamp_scenario1(self, mock_repo):
        #Entrambi i commit sono sospetti poichè precedenti al bug report

        # Configura dati di esempio
        mock_commit1 = MagicMock()
        mock_commit1.sha = 'commit1'
        mock_commit1.committed_date = 1635544000
        mock_commit1.author.name = 'author1'

        mock_commit2 = MagicMock()
        mock_commit2.sha = 'commit2'
        mock_commit2.committed_date = 1634336000
        mock_commit2.author.name = 'author2'

        mock_repo.commit.side_effect = [mock_commit1, mock_commit2]

        all_candidate_commits = [('commit1', 'author1'), ('commit2', 'author2')]
        issue_opened_at_timestamp = '2021-11-01T00:00:00Z'  #1635724800

        # Esegui la funzione di test
        result = extract_commit_by_timestamp(all_candidate_commits, issue_opened_at_timestamp)

        # Verifica che i commit siano estratti correttamente
        self.assertEqual(result, [('commit1', 'author1'), ('commit2', 'author2')])

    @patch('src.main.repo')
    def test_extract_commit_by_timestamp_scenario2(self, mock_repo):
        # Entrambi i commit non sono sospetti poichè successivi al bug report

        # Configura dati di esempio
        mock_commit1 = MagicMock()
        mock_commit1.sha = 'commit1'
        mock_commit1.committed_date = 1639544000
        mock_commit1.author.name = 'author1'

        mock_commit2 = MagicMock()
        mock_commit2.sha = 'commit2'
        mock_commit2.committed_date = 1637336000
        mock_commit2.author.name = 'author2'

        mock_repo.commit.side_effect = [mock_commit1, mock_commit2]

        all_candidate_commits = [('commit1', 'author1'), ('commit2', 'author2')]
        issue_opened_at_timestamp = '2021-11-01T00:00:00Z'  # 1635724800

        # Esegui la funzione di test
        result = extract_commit_by_timestamp(all_candidate_commits, issue_opened_at_timestamp)

        # Verifica che i commit siano estratti correttamente
        self.assertEqual(result, [])

    @patch('src.main.repo')
    def test_extract_commit_by_timestamp_scenario3(self, mock_repo):
        #Boundary Test

        # Configura dati di esempio
        mock_commit1 = MagicMock()
        mock_commit1.sha = 'commit1'
        mock_commit1.committed_date = 1635724801 #maggiore di 1 rispetto al timestamp dell'issue
        mock_commit1.author.name = 'author1'

        mock_commit2 = MagicMock()
        mock_commit2.sha = 'commit2'
        mock_commit2.committed_date = 1635724799 #minore di 1 rispetto al timestamp dell'issue
        mock_commit2.author.name = 'author2'

        mock_repo.commit.side_effect = [mock_commit1, mock_commit2]

        all_candidate_commits = [('commit1', 'author1'), ('commit2', 'author2')]
        issue_opened_at_timestamp = '2021-11-01T00:00:00Z'  # 1635724800

        # Esegui la funzione di test
        result = extract_commit_by_timestamp(all_candidate_commits, issue_opened_at_timestamp)

        # Verifica che i commit siano estratti correttamente
        self.assertEqual(result, [('commit2', 'author2')])

    @patch('src.main.repo')
    def test_extract_commit_by_timestamp_scenario4(self, mock_repo):
        # Timestamp dei commit uguali a quello realtivo all'issue

        # Configura dati di esempio
        mock_commit1 = MagicMock()
        mock_commit1.sha = 'commit1'
        mock_commit1.committed_date = 1635724800
        mock_commit1.author.name = 'author1'

        mock_commit2 = MagicMock()
        mock_commit2.sha = 'commit2'
        mock_commit2.committed_date = 1635724800
        mock_commit2.author.name = 'author2'

        mock_repo.commit.side_effect = [mock_commit1, mock_commit2]

        all_candidate_commits = [('commit1', 'author1'), ('commit2', 'author2')]
        issue_opened_at_timestamp = '2021-11-01T00:00:00Z'  # 1635724800

        # Esegui la funzione di test
        result = extract_commit_by_timestamp(all_candidate_commits, issue_opened_at_timestamp)

        # Verifica che i commit siano estratti correttamente
        self.assertEqual(result, [])

    @patch('src.main.issue_data', [{"number": 1, "created_at": "2022-01-01T00:00:00Z"}])
    @patch('src.main.get_bug_fix_commits_szz_issue')
    @patch('src.main.extract_issue_number')
    @patch('src.main.search_candidate_commit_szz')
    @patch('src.main.extract_commit_by_timestamp')
    @patch('src.main.print_candidate_commit')
    def test_szz_issue_valid(self, mock_print, mock_extract_commit, mock_search_commit, mock_extract_issue, mock_get_commits):
        # Configura dati di esempio
        mock_bug_fix_commit1 = MagicMock()
        mock_bug_fix_commit1.message = "Fixes #1"
        mock_bug_fix_commit1.hexsha = 'commit1'
        mock_bug_fix_commit1.created_at = '2022-01-01T00:00:00Z'

        mock_bug_fix_commits = [mock_bug_fix_commit1]

        mock_get_commits.return_value = mock_bug_fix_commits

        # Caso in cui l'issue è presente
        mock_extract_issue.return_value = 1
        mock_search_commit.return_value = [('commit2', 'author2')]

        issue_opened_at = '2023-10-30T00:00:00Z'  # timestamp 1635552000

        # Chiamata al metodo da testare
        szz_issue()

        # Verifica che i metodi siano stati chiamati correttamente
        mock_get_commits.assert_called_once()
        mock_extract_issue.assert_called_once()
        mock_search_commit.assert_called_once()
        mock_extract_commit.assert_called_once()
        mock_print.assert_called_once()

    @patch('src.main.issue_data', [])  # Lista vuota
    @patch('src.main.get_bug_fix_commits_szz_issue')
    @patch('src.main.extract_issue_number')
    @patch('src.main.search_candidate_commit_szz')
    @patch('src.main.extract_commit_by_timestamp')
    @patch('src.main.print_candidate_commit')
    def test_szz_issue_not_valid(self, mock_print, mock_extract_commit, mock_search_commit, mock_extract_issue, mock_get_commits):
        # Configura dati di esempio
        mock_bug_fix_commit1 = MagicMock()
        mock_bug_fix_commit1.message = "Fixes #1"
        mock_bug_fix_commit1.hexsha = 'commit1'
        mock_bug_fix_commit1.created_at = '2022-01-01T00:00:00Z'

        mock_bug_fix_commits = [mock_bug_fix_commit1]

        mock_get_commits.return_value = mock_bug_fix_commits

        # Caso in cui l'issue non è presente
        mock_extract_issue.return_value = None

        # Chiamata al metodo da testare
        szz_issue()

        # Verifica che i metodi siano stati chiamati correttamente
        mock_get_commits.assert_called_once()
        mock_extract_issue.assert_called_once()
        mock_search_commit.assert_not_called()  # Non dovrebbe essere chiamato senza un'issue valida
        mock_extract_commit.assert_not_called()  # Non dovrebbe essere chiamato senza un'issue valida
        mock_print.assert_called_once()


if __name__ == '__main__':
    unittest.main()
