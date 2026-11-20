import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
DEPLOYMENT = (ROOT / "docs" / "DEPLOYMENT.md").read_text(encoding="utf-8")


class ReleaseWorkflowTests(unittest.TestCase):
    def test_release_run_serializes_without_canceling_in_progress_run(self):
        self.assertIn("concurrency:", WORKFLOW)
        self.assertIn("group: release-${{ github.repository }}", WORKFLOW)
        self.assertIn("cancel-in-progress: false", WORKFLOW)

    def test_third_party_actions_are_pinned_to_full_shas(self):
        self.assertIn("actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09", WORKFLOW)
        self.assertIn("actions/setup-node@a0853c24544627f65ddf259abe73b1d18a591444", WORKFLOW)
        self.assertNotIn("actions/checkout@v", WORKFLOW)
        self.assertNotIn("actions/setup-node@v", WORKFLOW)

    def test_release_checkout_fetches_full_history_tags_and_notes(self):
        self.assertIn("fetch-depth: 0", WORKFLOW)
        self.assertIn("fetch-tags: true", WORKFLOW)
        self.assertIn("refs/notes/*:refs/notes/*", WORKFLOW)
        notes_step = WORKFLOW.split("- name: Fetch semantic-release notes", 1)[1].split("- name:", 1)[0]
        self.assertIn("continue-on-error: true", notes_step)

    def test_workflow_recovers_missing_releases_even_after_semantic_release_fails(self):
        self.assertIn("continue-on-error: true", WORKFLOW)
        self.assertIn("if: always()", WORKFLOW)
        self.assertIn("gh release create", WORKFLOW)
        self.assertIn("--generate-notes", WORKFLOW)
        self.assertIn("recovered_current_release", WORKFLOW)
        self.assertIn(
            'if [[ "$RELEASE_OUTCOME" == "failure" && "$RECOVERED_CURRENT_RELEASE" == "true" ]]; then',
            WORKFLOW,
        )

    def test_backfilled_release_is_latest_only_for_highest_semver_tag(self):
        recovery_step = WORKFLOW.split(
            "- name: Publish GitHub Releases missing for existing tags", 1
        )[1].split("- name:", 1)[0]
        self.assertIn("sort -V", recovery_step)
        self.assertIn("highest_version_tag", recovery_step)
        self.assertIn('if [[ "$tag" != "$highest_version_tag" ]]; then', recovery_step)
        self.assertIn("latest_option+=(--latest=false)", recovery_step)
        self.assertIn('"${latest_option[@]}"', recovery_step)

    def test_release_recovery_is_documented(self):
        self.assertIn("### Release", DEPLOYMENT)
        self.assertIn("refs/notes", DEPLOYMENT)
        self.assertIn("--generate-notes", DEPLOYMENT)
        self.assertIn("sort -V", DEPLOYMENT)
        self.assertIn("--latest=false", DEPLOYMENT)


if __name__ == "__main__":
    unittest.main()
