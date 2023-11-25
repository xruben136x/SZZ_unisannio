import unittest
from unittest.mock import MagicMock, patch
import re
from SZZ_unisannio.src.algorithm.main import get_bug_fix_commits_for_szz, generate_changes_dict, get_candidate_commits, \
    get_all_candidate_commits, extract_issue_number, match_comment, is_fix_contained   # Assicurati di sostituire 'your_script' con il nome reale del tuo script


class UnitTest(unittest.TestCase):

    def test_get_bug_fix_commits_for_szz_with_bug_and_fix(self):
        # Crea un mock per il repository
        mock_repo = MagicMock()

        # Crea alcuni commit mock con messaggi specifici per il testing
        mock_commits = [
            MagicMock(message="Fixing a bug"),
            MagicMock(message="Adding a new feature"),
            MagicMock(message="Fix: Another bug in the code")
        ]

        # Imposta la proprietà iter_commits del mock_repo
        mock_repo.iter_commits.return_value = mock_commits

        # Esegui la funzione di test
        bug_fix_commits = get_bug_fix_commits_for_szz(mock_repo)

        # Verifica che la funzione restituisca i commit corretti
        self.assertEqual(bug_fix_commits, [mock_commits[0], mock_commits[2]])

    def test_get_bug_fix_commits_for_szz_with_bug_and_fixed(self):
        # Crea un mock per il repository
        mock_repo = MagicMock()

        # Crea alcuni commit mock con messaggi specifici per il testing
        mock_commits = [
            MagicMock(message="Fixed a bug"),
            MagicMock(message="Adding a new feature"),
            MagicMock(message="Bug fix: Another bug in the code")
        ]

        # Imposta la proprietà iter_commits del mock_repo
        mock_repo.iter_commits.return_value = mock_commits

        # Esegui la funzione di test
        bug_fix_commits = get_bug_fix_commits_for_szz(mock_repo)

        # Verifica che la funzione restituisca i commit corretti
        self.assertEqual(bug_fix_commits, [mock_commits[0], mock_commits[2]])

    def test_get_bug_fix_commits_for_szz_with_fix_only(self):
        # Crea un mock per il repository
        mock_repo = MagicMock()

        # Crea alcuni commit mock con messaggi specifici per il testing
        mock_commits = [
            MagicMock(message="Fix #123456"),
            MagicMock(message="Fixing another issue"),
            MagicMock(message="Fix: Another problem in the code")
        ]

        # Imposta la proprietà iter_commits del mock_repo
        mock_repo.iter_commits.return_value = mock_commits

        # Esegui la funzione di test
        bug_fix_commits = get_bug_fix_commits_for_szz(mock_repo)

        # Verifica che la funzione restituisca una lista vuota
        self.assertEqual(bug_fix_commits, [])

    def test_get_bug_fix_commits_for_szz_with_bug_only(self):
        # Crea un mock per il repository
        mock_repo = MagicMock()

        # Crea alcuni commit mock con messaggi specifici per il testing
        mock_commits = [
            MagicMock(message="Bug #123456"),
            MagicMock(message="Fixing another issue"),
            MagicMock(message="Bug: Another problem in the code")
        ]

        # Imposta la proprietà iter_commits del mock_repo
        mock_repo.iter_commits.return_value = mock_commits

        # Esegui la funzione di test
        bug_fix_commits = get_bug_fix_commits_for_szz(mock_repo)

        # Verifica che la funzione restituisca una lista vuota
        self.assertEqual(bug_fix_commits, [])

    def test_get_bug_fix_commits_for_szz_with_empty_message(self):
        # Crea un mock per il repository
        mock_repo = MagicMock()

        # Crea alcuni commit mock con messaggi specifici per il testing
        mock_commits = [
            MagicMock(message=""),
            MagicMock(message=""),
            MagicMock(message="")
        ]

        # Imposta la proprietà iter_commits del mock_repo
        mock_repo.iter_commits.return_value = mock_commits

        # Esegui la funzione di test
        bug_fix_commits = get_bug_fix_commits_for_szz(mock_repo)

        # Verifica che la funzione restituisca una lista vuota
        self.assertEqual(bug_fix_commits, [])

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

    @patch('SZZ_unisannio.src.algorithm.main.args', recent=False)
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
    @patch('SZZ_unisannio.src.algorithm.main.commit_is_more_recent', side_effect=lambda x, y: True)
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
        with patch('SZZ_unisannio.src.algorithm.main.args', recent=True):
            result = get_candidate_commits(blame_result, file_path, changes_dict)

        expected_result = {('85ac1c6ddc93d4f53ff5b2c5c1c7bac7a8a44030', 'Sergey Kozub')}

        self.assertEqual(result, expected_result)

    @patch('SZZ_unisannio.src.algorithm.main.args', recent=False or True)
    def test_get_candidate_commits_no_changes(self, mock_args):
        blame_result = ""
        file_path = 'some/file/path'
        changes_dict = {'some/file/path': [2, 5]}

        expected_commits = set()

        commit_set = get_candidate_commits(blame_result, file_path, changes_dict)
        self.assertEqual(commit_set, expected_commits)

    @patch('SZZ_unisannio.src.algorithm.main.args', recent=False or True)
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

    @patch('SZZ_unisannio.src.algorithm.main.args', recent=False or True)
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

    @patch('SZZ_unisannio.src.algorithm.main.repo', autospec=True)
    @patch('SZZ_unisannio.src.algorithm.main.get_candidate_commits',
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

    @patch('SZZ_unisannio.src.algorithm.main.repo', autospec=True)
    @patch('SZZ_unisannio.src.algorithm.main.get_candidate_commits',
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

    @patch('SZZ_unisannio.src.algorithm.main.repo', autospec=True)
    @patch('SZZ_unisannio.src.algorithm.main.get_candidate_commits',
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


if __name__ == '__main__':
    unittest.main()
