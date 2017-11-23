""" test Observer client-server protocol
"""
import unittest
import json
from server.defs import Action, Result
from server.entity.Map import Map
from datetime import datetime
from .ServerConnection import run_in_foreground, ServerConnection


def dict_items(sequence):
            for item in sequence:
                yield item['idx'], item

class TestObserver(unittest.TestCase):
    """ Test class """

    @classmethod
    def setUpClass(cls):
        cls._conn = ServerConnection()

    @classmethod
    def tearDownClass(cls):
        #print('Close the socket')
        del cls._conn

    def test_0_connection(self):
        """ test connection """
        self.assertIsNotNone(self._conn._loop)
        self.assertIsNotNone(self._conn._reader)
        self.assertIsNotNone(self._conn._writer)

    def do_action(self, action, data):
        return run_in_foreground(
            self._conn.send_action(action, data)
            )

    def test_1_observer_get_game_list(self):
        """ connect as observer
            get list of recorded games
            verify list of games
        """
        result, message = self.do_action(Action.OBSERVER, None)
        self.assertEqual(Result.OKEY, result)
        self.assertNotEqual(len(message), 0)
        data = json.loads(message)
        self.assertNotEqual(len(data), 0)


    def getTrain(self, idx):
        result, message = self.do_action(Action.MAP, {'layer': 1})
        self.assertEqual(Result.OKEY, result)
        self.assertNotEqual(len(message), 0)
        data = json.loads(message)
        self.assertIn('train', data)
        self.assertGreater(len(data['train']), 0)
        train = {key: value for (key, value) in dict_items(data['train'])}
        self.assertIn(idx, train)
        return train[idx]


    def test_2_observer_select_game(self):
        """ select the test game
            verify initial state
        """
        result, message = self.do_action(Action.GAME, {'idx': 1})
        self.assertEqual(Result.OKEY, result)
        result, message = self.do_action(Action.MAP, {'layer': 0})
        self.assertEqual(Result.OKEY, result)
        self.assertNotEqual(len(message), 0)
        data = json.loads(message)
        self.assertNotEqual(len(data), 0)
        self.assertIn('line', data)

        line = {key: value for (key, value) in dict_items(data['line'])}
        self.assertEqual(line[1]["point"][0], 1)
        self.assertEqual(line[1]["point"][1], 7)
        train = self.getTrain(0)
        self.assertEqual(train['speed'], 0)
        self.assertIsNone(train['line_idx'])
        self.assertIsNone(train['position'])

    def set_turn(self, n):
        result, message = self.do_action(Action.TURN, {'idx': n})
        self.assertEqual(Result.OKEY, result)

    def test_3_observer_set_turn(self):
        """ set turn 3 and check position
            set turn 10 and check position
            set turn 0 and check position
            set turn 100 and check position
            set turn -1 and check position
        """
        self.set_turn(3)
        train = self.getTrain(0)
        self.assertEqual(train['speed'], 1)
        self.assertEqual(train['position'], 3)
        self.set_turn(10)
        train = self.getTrain(0)
        self.assertEqual(train['speed'], 0)
        self.assertEqual(train['position'], 10)
        self.set_turn(0)
        train = self.getTrain(0)
        self.assertEqual(train['speed'], 0)
        self.assertIsNone(train['position'])
        self.set_turn(100)
        train = self.getTrain(0)
        self.assertEqual(train['speed'], 0)
        self.assertEqual(train['position'], 10)
        self.set_turn(-1)
        train = self.getTrain(0)
        self.assertEqual(train['speed'], 0)
        self.assertIsNone(train['position'])


    def test_5_read_coordinates(self):
        """ get coordinates of points
            using layer 10
        """
        result, message = self.do_action(Action.MAP, {'layer': 10})
        self.assertEqual(Result.OKEY, result)
        self.assertNotEqual(len(message), 0)
        data = json.loads(message)
        self.assertIn('idx', data.keys())
        self.assertIn('coordinate', data.keys())
        self.assertIn('size', data.keys())
        self.assertNotIn('line', data.keys())
        self.assertNotIn('point', data.keys())


