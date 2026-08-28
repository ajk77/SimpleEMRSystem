"""Characterization tests for the research file-backed study/user/case flow.

Maps to docs/FUNCTIONALITY.md. Uses a temp copy of demo_study so tests never
write the committed resources/ tree. views.py binds dir_resources at import;
setUp patches SEMRinterface.views.dir_resources to that temp directory.
"""

import json
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import Client, TestCase

import SEMRinterface.views as views

FAMILIAR_COPY = (
    "Please use the available information to become familiar with this patient."
)
SELECT_COPY = (
    "Please select the information you used when preparing to present this case."
)


class DemoStudyFlowTests(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        src = Path(settings.BASE_DIR) / "resources" / "demo_study"
        shutil.copytree(src, self.tmp / "demo_study")
        self._orig = views.dir_resources
        views.dir_resources = str(self.tmp)
        self.client = Client(enforce_csrf_checks=True)
        self._real_results = (
            Path(settings.BASE_DIR) / "resources" / "demo_study" / "stored_results.txt"
        ).read_text()
        self._real_users = (
            Path(settings.BASE_DIR) / "resources" / "demo_study" / "user_details.json"
        ).read_text()

    def tearDown(self):
        views.dir_resources = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _obs_code(self):
        obs_path = self.tmp / "demo_study" / "cases_all" / "10000101" / "observations.json"
        keys = json.loads(obs_path.read_text())
        return "BUN" if "BUN" in keys else next(iter(keys))

    def _assert_committed_study_untouched(self):
        real = Path(settings.BASE_DIR) / "resources" / "demo_study"
        self.assertEqual((real / "stored_results.txt").read_text(), self._real_results)
        self.assertEqual((real / "user_details.json").read_text(), self._real_users)

    def test_eye_tracking_mode_defaults_on(self):
        self.assertTrue(settings.SEMR_EYE_TRACKING_MODE)

    def test_root_redirects_to_semrinterface(self):
        response = self.client.get("/")
        self.assertRedirects(
            response, "/SEMRinterface/", fetch_redirect_response=False
        )

    def test_study_list_contains_demo_study_without_login(self):
        response = self.client.get("/SEMRinterface/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "demo_study")
        self.assertNotIn("login", response.get("Location") or "")

    def test_user_list_contains_testUser1(self):
        response = self.client.get("/SEMRinterface/demo_study/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testUser1")

    def test_case_list_contains_assigned_10000101(self):
        response = self.client.get("/SEMRinterface/demo_study/testUser1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "10000101")
        self.assertContains(response, 'id="select10000101"')

    def test_familiar_viewer_has_instructions_demographics_and_observation_id(self):
        ob_code = self._obs_code()
        for path in (
            "/SEMRinterface/demo_study/testUser1/10000101/",
            "/SEMRinterface/demo_study/testUser1/10000101/0/",
        ):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertContains(response, FAMILIAR_COPY)
            html = response.content.decode()
            self.assertIn("age", html)
            self.assertIn("64", html)
            self.assertIn("Vitals", html)
            # Template calls add_observation_chart("BUN", ...); emr_3.js
            # builds id="rowBUN" / chartBUN from that key (JS is not executed here).
            self.assertIn(f'add_observation_chart("{ob_code}"', html)

    def test_select_epoch_has_select_copy_and_checkboxes(self):
        response = self.client.get("/SEMRinterface/demo_study/testUser1/10000101/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, SELECT_COPY)
        self.assertContains(response, "create_selection_screen")

    def test_post_selected_ids_appends_jsonl_in_temp_study_only(self):
        viewer = self.client.get("/SEMRinterface/demo_study/testUser1/10000101/")
        self.assertEqual(viewer.status_code, 200)
        csrftoken = self.client.cookies["csrftoken"].value

        results_path = self.tmp / "demo_study" / "stored_results.txt"
        before_lines = results_path.read_text().splitlines()

        response = self.client.post(
            "/SEMRinterface/selected_items/demo_study/testUser1/10000101/",
            data={"selected_ids": json.dumps(["rowBUN"])},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_X_CSRFTOKEN=csrftoken,
        )
        self.assertEqual(response.status_code, 200)

        after_lines = results_path.read_text().splitlines()
        self.assertEqual(len(after_lines), len(before_lines) + 1)
        record = json.loads(after_lines[-1])
        self.assertEqual(record["user_id"], "testUser1")
        self.assertEqual(record["case_id"], "10000101")
        self.assertEqual(record["selected_ids"], ["rowBUN"])
        self._assert_committed_study_untouched()

    def test_mark_complete_and_reset_update_temp_user_details(self):
        users_path = self.tmp / "demo_study" / "user_details.json"

        response = self.client.get(
            "/SEMRinterface/markcompleteurl/demo_study/testUser1/10000101/"
        )
        self.assertEqual(response.status_code, 200)
        users = json.loads(users_path.read_text())
        self.assertIn("10000101", users["testUser1"]["cases_completed"])

        response = self.client.get(
            "/SEMRinterface/casereset/",
            {"study_id": "demo_study", "user_id": "testUser1", "case_id": "10000101"},
        )
        self.assertEqual(response.status_code, 200)
        users = json.loads(users_path.read_text())
        self.assertNotIn("10000101", users["testUser1"]["cases_completed"])
        self._assert_committed_study_untouched()
