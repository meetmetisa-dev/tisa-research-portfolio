import unittest

from tisa_portfolio import cipherqoe, fedqoe, qoe_repro, trustflow


class QoEReproductionTests(unittest.TestCase):
    def test_group_split_has_no_subject_leakage(self):
        train, test = qoe_repro.grouped_split(qoe_repro.generate_sessions())
        self.assertFalse({row["subject_id"] for row in train} & {row["subject_id"] for row in test})

    def test_model_beats_constant_baseline(self):
        report = qoe_repro.run_experiment()
        self.assertLess(report["metrics"]["model_rmse"], report["metrics"]["baseline_rmse"])


class CipherQoETests(unittest.TestCase):
    def test_payload_is_never_modeled(self):
        report = cipherqoe.run_experiment()
        self.assertEqual(report["dataset"]["payload_bytes_inspected"], 0)
        self.assertNotIn("payload", cipherqoe.PUBLIC_METADATA_FIELDS)

    def test_metrics_are_bounded(self):
        report = cipherqoe.run_experiment()
        self.assertGreaterEqual(report["metrics"]["bitrate_class_accuracy"], 0.0)
        self.assertLessEqual(report["metrics"]["bitrate_class_accuracy"], 1.0)


class FederatedQoETests(unittest.TestCase):
    def test_training_reduces_error(self):
        report = fedqoe.run_experiment()
        self.assertLess(report["metrics"]["final_client_mean_rmse"], report["metrics"]["initial_client_mean_rmse"])
        self.assertGreater(report["metrics"]["communication_bytes"], 0)


class TrustFlowTests(unittest.TestCase):
    def test_alert_metrics_and_drift(self):
        report = trustflow.run_experiment()
        self.assertTrue(0.0 <= report["metrics"]["precision"] <= 1.0)
        self.assertTrue(0.0 <= report["metrics"]["recall"] <= 1.0)
        self.assertIsInstance(report["metrics"]["drift_flag"], bool)


if __name__ == "__main__":
    unittest.main()
