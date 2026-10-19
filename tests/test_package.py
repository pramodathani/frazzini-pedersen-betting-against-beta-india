"""Tests that the study's package installs and imports."""

import frazzini_pedersen_india


class TestPackage:
    """Checks on the installed package."""

    def test_package_has_docstring(self) -> None:
        """The package imports and describes itself.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the package has no docstring.
        """
        assert 'Betting Against Beta' in frazzini_pedersen_india.__doc__
