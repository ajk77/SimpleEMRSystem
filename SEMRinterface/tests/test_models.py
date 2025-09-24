"""
Unit tests for SEMRinterface models.
"""

import unittest
from datetime import datetime

try:
    from django.test import TestCase
    from ..models import Study, User, Case, Medication, CaseMedication, StoredResult, CaseSelection
    DJANGO_TESTING = True
except ImportError:
    DJANGO_TESTING = False
    TestCase = unittest.TestCase
    DJANGO_TESTING = True
except ImportError:
    DJANGO_TESTING = False
    TestCase = unittest.TestCase


class TestStudyModel(TestCase):
    """Test Study model."""

    def setUp(self):
        if not DJANGO_TESTING:
            self.skipTest("Django not available")

        self.study = Study.objects.create(
            study_id="test_study",
            data_layout={"layout": "test"},
            variable_details={"variables": "test"}
        )

    def tearDown(self):
        if DJANGO_TESTING:
            Study.objects.filter(study_id="test_study").delete()

    def test_study_creation(self):
        """Test study model creation."""
        self.assertEqual(self.study.study_id, "test_study")
        self.assertEqual(self.study.data_layout, {"layout": "test"})
        self.assertEqual(str(self.study), "test_study")

    def test_study_unique_constraint(self):
        """Test study ID uniqueness."""
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Study.objects.create(
                study_id="test_study",  # Same ID
                data_layout={"layout": "duplicate"}
            )


class TestUserModel(TestCase):
    """Test User model."""

    def setUp(self):
        if not DJANGO_TESTING:
            self.skipTest("Django not available")

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
            # Use a transaction-safe cleanup
            from django.db import transaction
            with transaction.atomic():
                User.objects.filter(study=self.study).delete()
                Study.objects.filter(study_id="test_study").delete()

    def test_user_creation(self):
        """Test user model creation."""
        self.assertEqual(self.user.user_id, "test_user")
        self.assertEqual(self.user.cases_assigned, ["case1", "case2"])
        self.assertEqual(self.user.cases_completed, ["case1"])
        self.assertEqual(str(self.user), "test_study:test_user")

    def test_user_unique_constraint(self):
        """Test user uniqueness within study."""
        with self.assertRaises(Exception):  # Should raise IntegrityError
            User.objects.create(
                study=self.study,
                user_id="test_user",  # Same user ID in same study
                cases_assigned=[],
                cases_completed=[]
            )

    def test_user_different_studies(self):
        """Test different user IDs can exist in different studies."""
        study2 = Study.objects.create(
            study_id="study2",
            data_layout={},
            variable_details={}
        )

        user2 = User.objects.create(
            study=study2,
            user_id="test_user2",  # Different user ID
            cases_assigned=[],
            cases_completed=[]
        )

        self.assertEqual(user2.user_id, "test_user2")
        self.assertEqual(user2.study, study2)

        # Cleanup
        study2.delete()


class TestCaseModel(TestCase):
    """Test Case model."""

    def setUp(self):
        if not DJANGO_TESTING:
            self.skipTest("Django not available")

        self.study = Study.objects.create(
            study_id="test_study",
            data_layout={},
            variable_details={}
        )
        self.case = Case.objects.create(
            study=self.study,
            case_id="test_case",
            demographics={"age": 30, "gender": "M"},
            observations={"bp": "120/80", "hr": 72},
            note_panel_data={"notes": "Patient stable"},
            case_details={"summary": "Test case"}
        )

    def tearDown(self):
        if DJANGO_TESTING:
            Case.objects.filter(study__study_id="test_study").delete()
            Study.objects.filter(study_id="test_study").delete()

    def test_case_creation(self):
        """Test case model creation."""
        self.assertEqual(self.case.case_id, "test_case")
        self.assertEqual(self.case.demographics["age"], 30)
        self.assertEqual(str(self.case), "test_study:test_case")

    def test_case_unique_constraint(self):
        """Test case uniqueness within study."""
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Case.objects.create(
                study=self.study,
                case_id="test_case",  # Same case ID in same study
                demographics={},
                observations={},
                note_panel_data={},
                case_details={}
            )


class TestMedicationModel(TestCase):
    """Test Medication model."""

    def setUp(self):
        if not DJANGO_TESTING:
            self.skipTest("Django not available")

        self.study = Study.objects.create(
            study_id="test_study",
            data_layout={},
            variable_details={}
        )
        self.medication = Medication.objects.create(
            study=self.study,
            medidx="MED001",
            display_name="Test Medication",
            original_name="TestMed",
            med_route="PO"
        )

    def tearDown(self):
        if DJANGO_TESTING:
            Medication.objects.filter(study__study_id="test_study").delete()
            Study.objects.filter(study_id="test_study").delete()

    def test_medication_creation(self):
        """Test medication model creation."""
        self.assertEqual(self.medication.medidx, "MED001")
        self.assertEqual(self.medication.display_name, "Test Medication")
        self.assertEqual(str(self.medication), "test_study:MED001")


class TestCaseMedicationModel(TestCase):
    """Test CaseMedication model."""

    def setUp(self):
        if not DJANGO_TESTING:
            self.skipTest("Django not available")

        self.study = Study.objects.create(
            study_id="test_study",
            data_layout={},
            variable_details={}
        )
        self.case = Case.objects.create(
            study=self.study,
            case_id="test_case",
            demographics={},
            observations={},
            note_panel_data={},
            case_details={}
        )
        self.medication = Medication.objects.create(
            study=self.study,
            medidx="MED001",
            display_name="Test Med",
            original_name="TestMed",
            med_route="PO"
        )
        self.case_medication = CaseMedication.objects.create(
            case=self.case,
            medication=self.medication,
            med_data=[{"time": "08:00", "dose": "10mg"}],
            y_axis_ranges={"min": 0, "max": 100}
        )

    def tearDown(self):
        if DJANGO_TESTING:
            CaseMedication.objects.filter(case__study__study_id="test_study").delete()
            Case.objects.filter(study__study_id="test_study").delete()
            Medication.objects.filter(study__study_id="test_study").delete()
            Study.objects.filter(study_id="test_study").delete()

    def test_case_medication_creation(self):
        """Test case medication model creation."""
        self.assertEqual(self.case_medication.case, self.case)
        self.assertEqual(self.case_medication.medication, self.medication)
        self.assertEqual(len(self.case_medication.med_data), 1)


if __name__ == '__main__':
    unittest.main()