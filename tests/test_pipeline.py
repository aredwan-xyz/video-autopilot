"""Regression coverage for completion status; no network or model calls."""
import json
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import Mock, patch

from src import llm, orchestrator, publish


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.manifest = self.root / "run-manifest.json"
        self.video = self.root / "final.mp4"
        self.metadata = self.root / "metadata.json"
        self.video.write_bytes(b"mock-video")
        self.metadata.write_text("{}")
        self.item = {"video": str(self.video), "metadata": str(self.metadata),
                     "result": {"status": "dry_run"}}

    def run_cli(self, effects, count=1):
        with patch.object(orchestrator, "channel_config", return_value={"publish": {}}), \
                patch.object(orchestrator, "make_one", side_effect=effects):
            return orchestrator.main(["--channel", "test", "--count", str(count),
                                      "--dry-run", "--manifest", str(self.manifest)])

    def test_provider_failure_fails_run_and_writes_manifest(self):
        self.assertEqual(self.run_cli([RuntimeError("provider down")]), 1)
        self.assertEqual(json.loads(self.manifest.read_text())["succeeded"], 0)
        self.assertFalse(orchestrator.verify_manifest(self.manifest))

    def test_partial_generation_is_failed(self):
        self.assertEqual(self.run_cli([self.item, RuntimeError("down")], 2), 1)
        self.assertEqual(json.loads(self.manifest.read_text())["succeeded"], 1)

    def test_missing_artifact_fails(self):
        self.video.unlink()
        self.assertEqual(self.run_cli([self.item]), 1)

    def test_empty_artifact_fails(self):
        self.video.write_bytes(b"")
        self.assertEqual(self.run_cli([self.item]), 1)

    def test_valid_dry_run_succeeds(self):
        self.assertEqual(self.run_cli([self.item]), 0)
        self.assertTrue(orchestrator.verify_manifest(self.manifest))

    def test_empty_channel_set_cannot_succeed(self):
        with patch.object(orchestrator, "all_channel_keys", return_value=[]):
            result = orchestrator.main(["--all", "--manifest", str(self.manifest)])
        self.assertEqual(result, 1)

    def test_duplicate_artifacts_cannot_satisfy_two_videos(self):
        self.assertEqual(self.run_cli([self.item, self.item], 2), 1)
        self.assertEqual(json.loads(self.manifest.read_text())["status"], "failed")

    def test_partial_publish_cannot_succeed(self):
        self.item["result"]["status"] = "partial_error"
        self.assertEqual(self.run_cli([self.item]), 1)

    def test_new_invocation_clears_previous_success(self):
        self.assertEqual(self.run_cli([self.item]), 0)
        self.assertEqual(self.run_cli([SystemExit("missing key")]), 1)
        self.assertEqual(json.loads(self.manifest.read_text())["status"], "failed")

    def test_manifest_detects_removed_artifact(self):
        self.run_cli([self.item])
        self.video.unlink()
        self.assertFalse(orchestrator.verify_manifest(self.manifest))

    def test_negative_count_rejected(self):
        with self.assertRaises(ValueError):
            self.run_cli([], -1)

    def test_assembly_failure_never_calls_publisher(self):
        cfg = {"channel": {"name": "test", "key": "test"}, "output_dir": "output"}
        with patch.object(orchestrator, "generate_idea", return_value={"title": "Demo"}), \
                patch.object(orchestrator, "write_script", return_value={"full_script": "text"}), \
                patch.object(orchestrator, "run_dir", return_value=self.root), \
                patch.object(orchestrator, "synthesize", return_value=self.root / "voice.mp3"), \
                patch.object(orchestrator, "ffprobe_duration", return_value=1), \
                patch.object(orchestrator, "gather_visuals"), \
                patch.object(orchestrator, "build_captions"), \
                patch.object(orchestrator, "assemble", return_value=self.root / "absent.mp4"), \
                patch.object(orchestrator, "publish") as post:
            with self.assertRaises(RuntimeError):
                orchestrator.make_one(cfg)
            post.assert_not_called()


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.cfg = {"publish": {"provider": "dry_run", "platforms": ["youtube", "tiktok"]},
                    "compliance": {"ai_disclosure": True}}

    def test_dry_run_does_not_contact_provider(self):
        with patch("requests.post") as request:
            self.assertEqual(publish.publish(self.cfg, Path("unused"), {"title": "Demo"})["status"], "dry_run")
            request.assert_not_called()

    def test_queue_is_distinct(self):
        self.cfg["publish"]["queue"] = True
        self.assertEqual(publish.publish(self.cfg, Path("unused"), {})["status"], "queued")

    def test_partial_platform_failure_is_not_posted(self):
        self.cfg["publish"]["provider"] = "ayrshare"
        upload = Mock(status_code=200)
        upload.json.return_value = {"url": "https://example.com/video.mp4"}
        good = Mock(status_code=200)
        good.json.return_value = {"status": "success"}
        bad = Mock(status_code=503)
        bad.json.return_value = {}
        with tempfile.NamedTemporaryFile() as video, patch.object(publish, "env", return_value="test"), \
                patch("requests.post", side_effect=[upload, good, bad]):
            result = publish.publish(self.cfg, Path(video.name), {"title": "Demo"})
        self.assertEqual(result["status"], "partial_error")
        self.assertEqual(result["results"]["youtube"], "submitted")

    def test_http_receipt_is_submitted_not_posted(self):
        self.cfg["publish"]["provider"] = "upload_post"
        receipt = Mock(status_code=202)
        receipt.json.return_value = {"status": "pending"}
        with tempfile.NamedTemporaryFile() as video, patch.object(publish, "env", return_value="test"), \
                patch("requests.post", return_value=receipt):
            result = publish.publish(self.cfg, Path(video.name), {"title": "Demo"})
        self.assertEqual(result["status"], "submitted")


class RetryTests(unittest.TestCase):
    class StatusError(Exception):
        def __init__(self, code, headers=None):
            self.status_code = code
            self.response = Mock(headers=headers or {})
            self.response.json.return_value = {}

    class ConnectionError(Exception):
        pass

    def setUp(self):
        # Exercise our retry policy without installing or contacting the provider SDK.
        self.sdk = patch.dict("sys.modules", {"openai": SimpleNamespace(
            APIStatusError=self.StatusError, APIConnectionError=self.ConnectionError)})
        self.sdk.start()
        self.addCleanup(self.sdk.stop)

    def test_503_retries_then_succeeds(self):
        call = Mock(side_effect=[self.StatusError(503), "ok"])
        with patch("time.sleep") as sleep:
            self.assertEqual(llm._with_retry(call, {"max_retries": 2}), "ok")
        self.assertEqual(call.call_count, 2)
        sleep.assert_called_once()

    def test_503_exhaustion_is_bounded(self):
        call = Mock(side_effect=self.StatusError(503, {"retry-after": "999"}))
        with patch("time.sleep") as sleep, self.assertRaises(self.StatusError):
            llm._with_retry(call, {"max_retries": 2})
        self.assertEqual(call.call_count, 3)
        self.assertTrue(all(c.args[0] <= 30 for c in sleep.call_args_list))

    def test_404_is_not_retried(self):
        call = Mock(side_effect=self.StatusError(404))
        with patch("time.sleep") as sleep, self.assertRaises(self.StatusError):
            llm._with_retry(call, {})
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
