import unittest

from analyzers.url_analyzer import analyze_url


class TestUrlAnalyzer(unittest.TestCase):
    def _has_signal(self, result, key):
        return any(s.get("key") == key and s.get("hit") for s in result.get("signals", []))

    def test_empty_url(self):
        result = analyze_url("")
        self.assertTrue(self._has_signal(result, "empty_url"))

    def test_invalid_url(self):
        result = analyze_url("not a url")
        self.assertTrue(self._has_signal(result, "invalid_url"))

    def test_ip_host(self):
        result = analyze_url("http://192.168.0.1/login")
        self.assertTrue(self._has_signal(result, "has_ip"))

    def test_shortener(self):
        result = analyze_url("https://bit.ly/abc123")
        self.assertTrue(self._has_signal(result, "shortener"))

    def test_suspicious_keyword(self):
        result = analyze_url("http://example.com/login")
        self.assertTrue(self._has_signal(result, "suspicious_keywords"))


if __name__ == "__main__":
    unittest.main()