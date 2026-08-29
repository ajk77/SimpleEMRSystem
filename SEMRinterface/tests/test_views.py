"""Characterization tests for the research file-backed study/user/case flow.

Maps to docs/FUNCTIONALITY.md. Uses a temp copy of demo_study so tests never
write the committed resources/ tree. views.py binds dir_resources at import;
setUp patches SEMRinterface.views.dir_resources to that temp directory.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

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
        self._runtime_file = self.tmp / "semr_runtime.json"
        self._runtime_patcher = patch(
            "SEMRinterface.lab_settings.runtime_path",
            return_value=str(self._runtime_file),
        )
        self._runtime_patcher.start()
        self._real_results = (
            Path(settings.BASE_DIR) / "resources" / "demo_study" / "stored_results.txt"
        ).read_text()
        self._real_users = (
            Path(settings.BASE_DIR) / "resources" / "demo_study" / "user_details.json"
        ).read_text()

    def tearDown(self):
        self._runtime_patcher.stop()
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

    def test_eye_tracking_mode_defaults_off(self):
        self.assertFalse(settings.SEMR_EYE_TRACKING_MODE)

    def test_home_screen_shows_unchecked_eye_tracking_toggle(self):
        response = self.client.get("/SEMRinterface/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lab settings")
        html = response.content.decode()
        self.assertIn('id="eye_tracking_mode"', html)
        self.assertNotIn(
            'id="eye_tracking_mode" value="1" checked',
            html,
        )

    def test_home_screen_saves_eye_tracking_mode(self):
        response = self.client.get("/SEMRinterface/")
        self.assertEqual(response.status_code, 200)
        csrftoken = self.client.cookies["csrftoken"].value
        response = self.client.post(
            "/SEMRinterface/",
            data={
                "csrfmiddlewaretoken": csrftoken,
                "eye_tracking_mode": "1",
                "save_settings": "1",
            },
        )
        self.assertRedirects(response, "/SEMRinterface/")
        self.assertTrue(self.client.session["SEMR_EYE_TRACKING_MODE"])
        saved = json.loads(self._runtime_file.read_text())
        self.assertTrue(saved["SEMR_EYE_TRACKING_MODE"])

        follow = self.client.get("/SEMRinterface/")
        html = follow.content.decode()
        self.assertIn('id="eye_tracking_mode" value="1" checked', html)

        csrftoken = self.client.cookies["csrftoken"].value
        response = self.client.post(
            "/SEMRinterface/",
            data={
                "csrfmiddlewaretoken": csrftoken,
                "save_settings": "1",
            },
        )
        self.assertRedirects(response, "/SEMRinterface/")
        self.assertFalse(self.client.session["SEMR_EYE_TRACKING_MODE"])
        saved = json.loads(self._runtime_file.read_text())
        self.assertFalse(saved["SEMR_EYE_TRACKING_MODE"])

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
        html = response.content.decode()
        self.assertNotIn("127.0.0.1", html)
        self.assertIn("/SEMRinterface/demo_study/", html)
        self.assertIn("jquery-3.6.4", html)

    def test_user_list_contains_testUser1(self):
        response = self.client.get("/SEMRinterface/demo_study/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testUser1")
        html = response.content.decode()
        self.assertNotIn("127.0.0.1", html)
        self.assertIn("/SEMRinterface/demo_study/testUser1/", html)

    def test_case_list_contains_assigned_10000101(self):
        response = self.client.get("/SEMRinterface/demo_study/testUser1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "10000101")
        self.assertContains(response, 'id="select10000101"')
        html = response.content.decode()
        self.assertNotIn("127.0.0.1", html)
        self.assertIn("/SEMRinterface/demo_study/testUser1/10000101/", html)

    def test_unmounted_2024_2_routes_return_404(self):
        for path in (
            "/SEMRinterface/login/",
            "/SEMRinterface/welcome/",
            "/SEMRinterface/select/",
            "/SEMRinterface/api/info/",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 404)

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
            # Observation keys are embedded via json_script; emr_3.js still
            # builds id="rowBUN" / chartBUN from those keys (JS is not executed here).
            self.assertIn(f'"{ob_code}"', html)
            self.assertIn('type="application/json"', html)
            self.assertIn('id="case-observations"', html)
            self.assertIn("init_case_viewer", html)
            self.assertNotIn("autoescape", html)
            self.assertNotIn("add_observation_chart(", html)

        template_src = (
            Path(settings.BASE_DIR)
            / "SEMRinterface"
            / "templates"
            / "SEMRinterface"
            / "case_viewer.html"
        ).read_text()
        self.assertNotIn("{% autoescape", template_src)
        self.assertNotIn("endautoescape", template_src)

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
