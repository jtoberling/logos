"""
Unit tests for LogosConstitution.

Tests the constitution loader and personality foundation.
"""

import pytest
from unittest.mock import patch, mock_open

from src.personality.constitution import LogosConstitution


class TestLogosConstitution:
    """Test LogosConstitution functionality."""

    def test_initialization_loads_manifesto(self):
        """Test that constitution loads the manifesto on initialization."""
        manifesto_content = "# THE LOGOS MANIFESTO\n\nI. Reason over Mimicry\n\nLogos is..."

        with patch('builtins.open', mock_open(read_data=manifesto_content)):
            constitution = LogosConstitution()

            assert constitution.manifesto_content == manifesto_content
            assert "THE LOGOS MANIFESTO" in constitution.get_constitution()

    def test_initialization_handles_missing_file(self):
        """Test that constitution handles missing manifesto file gracefully."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            constitution = LogosConstitution()

            assert constitution.manifesto_content == ""
            assert "Logos" in constitution.get_constitution()  # Fallback content

    def test_get_constitution_includes_identity(self):
        """Test that constitution includes identity information."""
        with patch('builtins.open', mock_open(read_data="")):
            constitution = LogosConstitution()

            const = constitution.get_constitution()
            assert "Logos" in const
            assert "digital personality" in const
            assert "János" in const

    def test_get_constitution_includes_principles(self):
        """Test that constitution includes core principles."""
        with patch('builtins.open', mock_open(read_data="")):
            constitution = LogosConstitution()

            const = constitution.get_constitution()
            assert "reason" in const.lower()
            assert "logic" in const.lower()
            assert "transparency" in const.lower()

    def test_get_constitution_includes_relationship(self):
        """Test that constitution defines relationship dynamics."""
        with patch('builtins.open', mock_open(read_data="")):
            constitution = LogosConstitution()

            const = constitution.get_constitution()
            assert "partner" in const.lower()
            assert "collaborative" in const.lower() or "partnership" in const.lower()

    def test_get_constitution_includes_manifesto(self):
        """Test that constitution includes manifesto content."""
        manifesto_content = "THE LOGOS MANIFESTO\nI. Reason over Mimicry"

        with patch('builtins.open', mock_open(read_data=manifesto_content)):
            constitution = LogosConstitution()

            const = constitution.get_constitution()
            assert "THE LOGOS MANIFESTO" in const
            assert "Reason over Mimicry" in const

    def test_get_constitution_structured_format(self):
        """Test that constitution has proper structure."""
        with patch('builtins.open', mock_open(read_data="")):
            constitution = LogosConstitution()

            const = constitution.get_constitution()

            # Should have clear sections
            assert "IDENTITY:" in const
            assert "CORE PRINCIPLES:" in const
            assert "RELATIONSHIP DYNAMICS:" in const
            assert "COMMUNICATION STYLE:" in const

    def test_get_constitution_no_duplicates(self):
        """Test that constitution doesn't have duplicate content."""
        manifesto_content = "I. Reason over Mimicry\n\nLogos is not an imitation..."

        with patch('builtins.open', mock_open(read_data=manifesto_content)):
            constitution = LogosConstitution()

            const = constitution.get_constitution()

            # Count occurrences of key phrases
            reason_count = const.count("Reason over Mimicry")
            assert reason_count == 1, "Manifesto content should not be duplicated"

    def test_add_principle(self):
        """Test adding new principles to constitution."""
        with patch('builtins.open', mock_open(read_data="")):
            constitution = LogosConstitution()

            # Add a new principle
            constitution.add_principle("Test Principle", "This is a test principle.")

            const = constitution.get_constitution()
            assert "Test Principle" in const
            assert "This is a test principle" in const

    def test_add_principle_validation(self):
        """Test that add_principle validates input."""
        with patch('builtins.open', mock_open(read_data="")):
            constitution = LogosConstitution()

            # Should raise error for empty inputs
            with pytest.raises(ValueError):
                constitution.add_principle("", "content")

            with pytest.raises(ValueError):
                constitution.add_principle("title", "")

    def test_constitution_immutable_by_default(self):
        """Test that constitution content is stable."""
        with patch('builtins.open', mock_open(read_data="Manifesto v1")):
            constitution = LogosConstitution()

            const1 = constitution.get_constitution()
            const2 = constitution.get_constitution()

            assert const1 == const2  # Should be consistent

    def test_get_constitution_length_reasonable(self):
        """Test that constitution is appropriately sized."""
        with patch('builtins.open', mock_open(read_data="Short manifesto")):
            constitution = LogosConstitution()

            const = constitution.get_constitution()

            # Should be substantial but not enormous
            assert len(const) > 500  # At least 500 characters
            assert len(const) < 10000  # Less than 10k characters