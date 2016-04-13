# -*- coding: utf-8 -*-
import time
import unittest
from datetime import datetime, timedelta

from knurld_sdk.APIManager import TokenGetter, AppModel, Consumer, Enrollment, Analysis
from knurld_sdk import helpers as h
from knurld_sdk.CustomExceptions import ImproperArgumentsException


def temp_token():
    # obtain a valid admin token
    tg = TokenGetter()
    return tg.get_token()


class TestVerification(unittest.TestCase):
    pass


class TestEnrollment(unittest.TestCase):

    model_id = '3c1bbea5f380bcbfef6910e0c879bd04'  # "boston", "chicago", "san francisco"
    consumer_id = '3c1bbea5f380bcbfef6910e0c879bf82'  # M theo walcott
    enrollment_id = '5571c3a5c203f17826740e9019832ff8'  # M theo walcott
    e = Enrollment(temp_token(), model_id, consumer_id)

    hosted_audio_url = 'https://www.dropbox.com/s/uawm0lb0p3zl4nj/enrollment.wav?dl=1'

    def test_create(self):
        response = self.e.create()
        print(response)
        self.assertIsNotNone(response)

    def test_update(self):
        intervals = list()
        response = self.e.update(self.enrollment_id, wav_file=self.hosted_audio_url, intervals=intervals)

    """
    def test_get(self):
        response = self.e.get_enrollment()
        self.assertIsNotNone(response.get('items'))

        enrollment_id = 'a67a3f337823e2d56ec264f8c3d6ceb5'
        _ = self.e.get_enrollment(enrollment_id)
        self.assertRegexpMatches(self.e.enrollment_id, h.regx_pattern_id())
        self.assertIsNotNone(self.e.get_enrollment(enrollment_id).get('instructions'))

    def test_get_consumer_token(self):
        user = 'alexis'
        pswd = 'sanchez'
        consumer_token = self.e.get_consumer_token(user, pswd)
        self.assertRegexpMatches(consumer_token, h.regx_pattern_id(count=342))
    """


class TestAnalysis(unittest.TestCase):

    hosted_audio_url = 'https://www.dropbox.com/s/uawm0lb0p3zl4nj/enrollment.wav?dl=1'
    model_id = '3c1bbea5f380bcbfef6910e0c879bd04'  # "boston", "chicago", "san francisco"
    # consumer = Consumer(temp_token(), username='theo', password='walcott')  # M theo walcott

    @property
    def analysis(self):
        a = Analysis(temp_token(), self.model_id, self.consumer, self.hosted_audio_url, num_words=3)
        return a

    def test_start_task(self):
        result = self.analysis.start_task()
        self.assertIsNotNone(result)
        self.assertEqual(result.get('taskStatus'), 'started')
        self.assertRegexpMatches(result.get('taskName'), h.regx_pattern_id())

    def test_check_status(self):
        result = self.analysis.start_task()
        test_task_name = result.get('taskName')
        result = self.analysis.check_status(test_task_name)
        self.assertIsNotNone(result)
        self.assertIn(result.get('taskStatus'), ['running', 'completed'])

    def test_execute_step(self):
        result = self.analysis.execute_step()
        print(result)


class TestConsumer(unittest.TestCase):

    p = {
        # a unique username for testing
        "username": 'theo_' + str(datetime.now()),
        "password": 'walcott',
        "gender": 'M'
    }
    c = Consumer(token=temp_token(), payload=p)

    def test_create(self):
        consumer = self.c.create()
        self.assertRegexpMatches(consumer, h.regx_pattern_id())

    def test_update(self):
        p = {
            # a unique username for testing
            "username": 'theo_' + str(datetime.now()) + '_alias',
            "password": 'walcott',
            "gender": 'M'
        }
        c_alias = Consumer(token=temp_token(), payload=p)
        test_consumer_id = c_alias.create()
        p = {
            "password": 'walcott360'
        }
        consumer = c_alias.update(test_consumer_id, payload_override=p)
        self.assertRegexpMatches(consumer, h.regx_pattern_id())

    def test_get(self):
        p = {
            # a unique username for testing
            "username": 'theo_' + str(datetime.now()) + '_alias',
            "password": 'walcott',
            "gender": 'M'
        }
        c_alias = Consumer(token=temp_token(), payload=p)
        test_consumer_id = c_alias.create()
        result = c_alias.get(test_consumer_id)
        self.assertIsNotNone(result.get('href'))

    def test_get_all(self):
        result = self.c.get_all()
        self.assertIsNotNone(result.get('items'))

    def delete(self):
        pass


class TestAppModel(unittest.TestCase):
    p = {
        "vocabulary": ["boston", "chicago", "pyramid"],
        "verificationLength": 3,
        "enrollmentRepeats": 3
    }
    am = AppModel(temp_token(), payload=p)
    test_app_model_id = am.create()

    def test_bad_payload(self):
        payload = {
            "vocabulary": ["boston", "chicago", "pyramid"],
            "enrollmentRepeats": 3
        }
        self.assertIsNone(self.am.set_payload(payload))

    def test_good_payload(self):
        payload = {
            "vocabulary": ["boston", "chicago", "pyramid"],
            "verificationLength": 3,
            "enrollmentRepeats": 3
        }
        self.assertIsNotNone(self.am.set_payload(payload))

    def test_create(self):
        self.assertRegexpMatches(self.test_app_model_id, h.regx_pattern_id())

    def test_update(self):
        self.assertRegexpMatches(self.test_app_model_id, h.regx_pattern_id())

        payload = {
            "enrollmentRepeats": 3,
            "threshold": 0,
            "autoThresholdEnable": False,
            "autoThresholdClearance": 0,
            "autoThresholdMaxRise": 0,
            "useModelUpdate": False,
            "modelUpdateDailyLimit": 0
        }
        app_model_id = self.am.update(app_model_id=self.test_app_model_id, payload_override=payload)
        self.assertRegexpMatches(app_model_id, h.regx_pattern_id())

    def test_get(self):
        result = self.am.get(self.test_app_model_id)
        self.assertIsNotNone(result.get('href'))

    def test_get_all(self):
        result = self.am.get_all()
        self.assertIsNotNone(result.get('items'))

    def delete(self):
        pass


class TestTokenGetter(unittest.TestCase):

    tg = TokenGetter()

    def test_renew_access_token(self):

        # new token must be the one just got fetched using remote APIs
        token = self.tg.renew_access_token()
        self.assertEqual(self.tg._token, token)

    def test_is_valid_token(self):

        # set up for an unexpired token (assuming self.tg object is created just a moments ago, this is a valid token)
        self.tg.renew_access_token()
        is_valid = self.tg._is_valid_token(self.tg._token)
        self.assertEqual(True, is_valid)

        # set up for an expired token
        self.tg._token_timestamp = datetime.now() - timedelta(seconds=3600)

        # the current token may or may not be valid based on the tg timestamp
        is_valid = self.tg._is_valid_token(self.tg._token)
        self.assertEqual(False, is_valid)

    def test_get_token(self):
        # set up for an expired token
        cur_token = self.tg._token
        new_token = self.tg.get_token()
        self.assertNotEqual(cur_token, new_token)

        # set up for an unexpired token (assuming self.tg object is created just a moments ago, this is a valid token)
        self.assertEqual(new_token, self.tg.get_token())

    def token_renew_frequency(self):
        """
        With this test, a token is set to expire every 10 seconds
        Fetches and prints a token at 2 seconds interval
        Assert that we get two unique tokens
        TODO: This is actually a functional test which needs to be placed at more appropriate location
        """
        until = 10
        interval = 2

        # get the token that expires in 10 seconds
        self.tg = TokenGetter(expires=10)

        tokens = []
        # check if the token expires properly in set interval and the new toke is successfully fetched after expiry only
        for i in range(1, until):
            time.sleep(interval)

            # fetch token
            token = self.tg.get_token()
            print('TOKEN: ---> ' + str(token))

            # put it in the list
            tokens.append(token)

        # assert for exactly two unique tokens during 10 * 2 = 20 seconds of overall time
        self.assertEquals(len(set(tokens)), 2)


if __name__ == '__main__':
    unittest.main()
