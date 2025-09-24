"""
Unit tests for SEMRinterface services.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Test the services in both Django and non-Django contexts
try:
    from django.test import TestCase
    from ..models import Study, User, Case, Medication, CaseMedication
    from ..services import (
        load_json, save_json, get_study_ids, get_user_details,
        get_case_assignments, update_case_assignments, get_case_files,
        _get_study_or_none, _parse_datetime_value, _serialize_user_details
    )
    DJANGO_TESTING = True
except ImportError:
    # Fallback for non-Django testing
    DJANGO_TESTING = False
    TestCase = unittest.TestCase

    # Mock the imports
    class MockStudy:
        objects = MagicMock()

    class MockUser:
        objects = MagicMock()

    # Import with mocks
    with patch('SEMRinterface.services.Study', MockStudy), \
         patch('SEMRinterface.services.User', MockUser):
        from ..services import (
            load_json, save_json, get_study_ids, get_user_details,
            get_case_assignments, update_case_assignments, get_case_files,
            _get_study_or_none, _parse_datetime_value, _serialize_user_details
        )


class TestJSONUtilities(TestCase):
    """Test JSON loading and saving utilities."""

    def setUp(self):
        self.test_data = {"key": "value", "number": 42}
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_load_json_success(self):
        """Test successful JSON loading."""
        with open(self.temp_file.name, 'w') as f:
            json.dump(self.test_data, f)

        result = load_json(self.temp_file.name)
        self.assertEqual(result, self.test_data)

    def test_load_json_file_not_found(self):
        """Test loading non-existent file."""
        result = load_json("nonexistent.json")
        self.assertIsNone(result)

    def test_load_json_invalid_json(self):
        """Test loading invalid JSON."""
        with open(self.temp_file.name, 'w') as f:
            f.write("invalid json")

        result = load_json(self.temp_file.name)
        self.assertIsNone(result)

    def test_save_json(self):
        """Test JSON saving."""
        save_json(self.test_data, self.temp_file.name)

        with open(self.temp_file.name, 'r') as f:
            loaded = json.load(f)

        self.assertEqual(loaded, self.test_data)


class TestStudyOperations(TestCase):
    """Test study-related operations."""

    def setUp(self):
        if DJANGO_TESTING:
            # Create test study
            self.study = Study.objects.create(
                study_id="test_study",
                data_layout={"layout": "test"},
                variable_details={"vars": "test"}
            )

    def tearDown(self):
        if DJANGO_TESTING:
            Study.objects.all().delete()

    @patch('SEMRinterface.services.Study')
    def test_get_study_ids_database(self, mock_study):
        """Test getting study IDs from database."""
        if not DJANGO_TESTING:
            self.skipTest("Django not available")

        mock_study.objects.values_list.return_value = ["study1", "study2"]
        result = get_study_ids()
        self.assertEqual(result, ["study1", "study2"])

    def test_get_study_ids_filesystem(self):
        """Test getting study IDs from filesystem."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test directories
            os.makedirs(os.path.join(temp_dir, "study1"))
            os.makedirs(os.path.join(temp_dir, "study2"))
            os.makedirs(os.path.join(temp_dir, "not_a_study.txt"))

            result = get_study_ids(temp_dir)
            self.assertEqual(sorted(result), ["study1", "study2"])


class TestUserOperations(TestCase):
    """Test user-related operations."""

    def setUp(self):
        if DJANGO_TESTING:
            self.study = Study.objects.create(
                study_id="test_study",
                data_layout={},
                variable_details={}
            )
            self.user = User.objects.create(
                study=self.study,
                user_id="test_user",
                cases_assigned=["case1", "case2"],
                cases_completed=["case1"]
            )

    def tearDown(self):
        if DJANGO_TESTING:
            User.objects.all().delete()
            Study.objects.all().delete()

    def test_parse_datetime_value_none(self):
        """Test parsing None datetime value."""
        result = _parse_datetime_value(None)
        self.assertIsNone(result)

    def test_parse_datetime_value_string(self):
        """Test parsing string datetime value."""
        if DJANGO_TESTING:
            test_str = "2023-01-01T00:00:00Z"
            result = _parse_datetime_value(test_str)
            self.assertIsInstance(result, datetime)

    def test_parse_datetime_value_timestamp(self):
        """Test parsing timestamp datetime value."""
        timestamp = 1672531200.0  # 2023-01-01 00:00:00 UTC
        result = _parse_datetime_value(timestamp)
        self.assertIsInstance(result, datetime)

    @patch('SEMRinterface.services.DJANGO_AVAILABLE', True)
    @patch('SEMRinterface.services.Study')
    @patch('SEMRinterface.services.User')
    def test_get_user_details_database(self, mock_user, mock_study):
        """Test getting user details from database."""
        if not DJANGO_TESTING:
            self.skipTest("Django not available")

        # Mock the database objects
        mock_study_obj = MagicMock()
        mock_study.objects.get.return_value = mock_study_obj

        mock_user_obj = MagicMock()
        mock_user_obj.user_id = "user1"
        mock_user_obj.last_accessed = None
        mock_user_obj.cases_assigned = ["case1"]
        mock_user_obj.cases_completed = ["case1"]
        mock_user.objects.filter.return_value = [mock_user_obj]

        result = get_user_details("test_study")
        self.assertIsInstance(result, dict)
        self.assertIn("user1", result)


class TestCaseOperations(TestCase):
    """Test case-related operations."""

    def setUp(self):
        if DJANGO_TESTING:
            self.study = Study.objects.create(
                study_id="test_study",
                data_layout={},
                variable_details={}
            )
            self.case = Case.objects.create(
                study=self.study,
                case_id="test_case",
                demographics={"age": 30},
                observations={"bp": "120/80"},
                note_panel_data={"notes": "test"},
                case_details={"summary": "test case"}
            )

    def tearDown(self):
        if DJANGO_TESTING:
            Case.objects.all().delete()
            Study.objects.all().delete()

    def test_get_case_files_filesystem(self):
        """Test getting case files from filesystem."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create case directory structure
            case_dir = os.path.join(temp_dir, "test_study", "cases_all", "test_case")
            os.makedirs(case_dir)

            # Create test files
            test_data = {"test": "data"}
            with open(os.path.join(case_dir, "demographics.json"), 'w') as f:
                json.dump(test_data, f)

            result = get_case_files("test_study", "test_case", temp_dir)
            self.assertIsInstance(result, dict)
            self.assertIn("demographics", result)


if __name__ == '__main__':
    unittest.main()