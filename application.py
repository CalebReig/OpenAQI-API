"""
This is the forecasts file for the application.
FLASK_APP environment variable should be set to this file
"""
from app import create_app
import click
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

#creates the app with the given config
application = create_app(os.getenv('FLASK_CONFIG'))


#command for running unittests
@application.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
