"""
Unit test for the construct_model module
"""

from illuminator.core.model_constructor import ModelConstructor


class TestConstructModel:
    """
    Test for the abstract class 
    """

    def test_abstract_class(self):
        """
        Test that the abstract class cannot be instantiated
        """
        # TODO: Implement this test
        pass


    # TODO: this should be part of a test when registering a model in the library
    def validate_args(self, *args) -> None:
        """
        Validates the arguments passed to the compute_step method
        """
        for arg in args:
            if arg not in self.inputs or arg not in self.outputs or arg not in self.states:
                raise ValueError(f"{arg} is not a valid argument")