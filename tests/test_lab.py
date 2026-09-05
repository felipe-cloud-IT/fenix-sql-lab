import unittest

import app
from catalog import CATALOG, public_catalog


class CatalogTests(unittest.TestCase):
    def test_catalog_has_150_unique_lessons(self):
        self.assertEqual(len(CATALOG), 150)
        self.assertEqual(len({x.id for x in CATALOG}), 150)
        self.assertEqual(len({x.solution_sql for x in CATALOG}), 150)

    def test_all_reference_queries_execute(self):
        for lesson in CATALOG:
            with self.subTest(lesson=lesson.id):
                app.run_sql(lesson.solution_sql)

    def test_public_catalog_hides_answers_and_hints(self):
        for lesson in public_catalog(CATALOG):
            self.assertNotIn("solution_sql", lesson)
            self.assertNotIn("required", lesson)
            self.assertNotIn("hints", lesson)


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.app.test_client()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["exercises"], 150)

    def test_reference_answer_passes(self):
        lesson = CATALOG[0]
        response = self.client.post("/api/query", json={"lesson_id": 1, "sql": lesson.solution_sql})
        self.assertTrue(response.get_json()["evaluation"]["passed"])

    def test_incomplete_answer_does_not_pass(self):
        response = self.client.post("/api/query", json={"lesson_id": 5, "sql": "SELECT tipo FROM equipos;"})
        self.assertFalse(response.get_json()["evaluation"]["passed"])

    def test_sql_writes_are_rejected(self):
        for sql in ("INSERT INTO equipos(id) VALUES(999);", "UPDATE equipos SET estado='x';", "DELETE FROM equipos;", "DROP TABLE equipos;"):
            with self.subTest(sql=sql):
                response = self.client.post("/api/query", json={"lesson_id": 1, "sql": sql})
                self.assertEqual(response.status_code, 400)
                self.assertFalse(response.get_json()["ok"])

    def test_multiple_statements_are_rejected(self):
        response = self.client.post("/api/query", json={"lesson_id": 1, "sql": "SELECT nombre FROM equipos; SELECT tipo FROM equipos;"})
        self.assertEqual(response.status_code, 400)

    def test_friendly_syntax_error(self):
        response = self.client.post("/api/query", json={"lesson_id": 5, "sql": "SELECT tipo y estado FROM equipos;"})
        self.assertIn("Revisa comas", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
