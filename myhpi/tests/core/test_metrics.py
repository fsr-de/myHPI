from myhpi.tests.core.utils import MyHPIPageTestCase


class MetricsTests(MyHPIPageTestCase):
    def test_unauthorized_metrics(self):
        with self.settings(METRICS_API_KEY="TEST_KEY"):
            response = self.client.get("/metrics")
            self.assertEqual(response.status_code, 401)

    def test_authorized_metrics(self):
        with self.settings(METRICS_API_KEY="TEST_KEY"):
            response = self.client.get("/metrics", **{"HTTP_X-API-KEY": "TEST_KEY"})
            self.assertEqual(response.status_code, 200)
