from unittest import TestCase

from file_manager.operations import Insert


class InsertInsertTestCase(TestCase):
    def setUp(self) -> None:
        self.text = "Michael Scofield"

    def test_insert_before(self):
        # prev_ins = {}, current_ins = []
        # [\\\] {///}
        prev_insert = Insert(8, "J. ")
        current_text = prev_insert.execute(self.text)
        current_insert = Insert(0, "origami ")
        current_text = (current_insert / prev_insert).execute(current_text)
        self.assertEqual(current_text, "origami Michael J. Scofield")

    def test_insert_to_same_position(self):
        prev_insert = Insert(0, "ami ")
        current_text = prev_insert.execute(self.text)
        current_insert = Insert(0, "orig")
        current_text = (current_insert / prev_insert).execute(current_text)
        self.assertEqual(current_text, "origami Michael Scofield")

    def test_insert_after(self):
        # prev_ins = {}, current_ins = []
        # {  }[  ]
        prev_insert = Insert(0, "origami ")
        current_text = prev_insert.execute(self.text)
        current_insert = Insert(8, "J. ")
        current_text = (current_insert / prev_insert).execute(current_text)
        self.assertEqual(current_text, "origami Michael J. Scofield")
