"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
      #  app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

   # @classmethod
    def setUp(self):
        """Runs before each test"""
       # db.session.query(Account).delete()  # clean up the last tests
    #    db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    def test_get_account_list(self):
        """It should Get a list of Accounts"""
        self._create_accounts(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    ######################################################################
    # UPDATE AN EXISTING ACCOUNT
    ######################################################################
    @app.route("/accounts/<int:account_id>", methods=["PUT"])
    def update_accounts(account_id):
        """
        Update an Account
        This endpoint will update an Account based on the posted data
        """
        app.logger.info("Request to update an Account with id: %s", account_id)

        account = Account.find(account_id)
        if not account:
            abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account_id}] could not be found.")

        account.deserialize(request.get_json())
        account.update()

        return account.serialize(), status.HTTP_200_OK
 
        ######################################################################
    # DELETE AN ACCOUNT
    ######################################################################
    @app.route("/accounts/<int:account_id>", methods=["DELETE"])
    def delete_accounts(account_id):
        """
        Delete an Account
        This endpoint will delete an Account based on the account_id that is requested
        """
        app.logger.info("Request to delete an Account with id: %s", account_id)

        account = Account.find(account_id)
        if account:
            account.delete()

        return "", status.HTTP_204_NO_CONTENT

        ######################################################################
    # LIST ALL ACCOUNTS
    ######################################################################
    @app.route("/accounts", methods=["GET"])
    def list_accounts():
        """
        List all Accounts
        This endpoint will list all Accounts
        """
        app.logger.info("Request to list Accounts")

        accounts = Account.all()
        account_list = [account.serialize() for account in accounts]

        app.logger.info("Returning [%s] accounts", len(account_list))
        return jsonify(account_list), status.HTTP_200_OK
    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ADD YOUR TEST CASES HERE ...
