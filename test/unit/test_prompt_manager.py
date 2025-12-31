"""
Unit tests for LogosPromptManager.

Tests the prompt manager that combines constitution and RAG context.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.personality.prompt_manager import LogosPromptManager


class TestLogosPromptManager:
    """Test LogosPromptManager functionality."""

    def test_initialization_with_constitution(self):
        """Test that prompt manager initializes with constitution."""
        with patch('src.personality.prompt_manager.LogosConstitution') as mock_constitution:
            mock_const_instance = MagicMock()
            mock_const_instance.get_constitution.return_value = "Test constitution"
            mock_constitution.return_value = mock_const_instance

            pm = LogosPromptManager()

            mock_constitution.assert_called_once()
            assert pm.constitution == mock_const_instance

    def test_get_constitution_delegates_to_constitution_loader(self):
        """Test that get_constitution delegates to the constitution loader."""
        with patch('src.personality.prompt_manager.LogosConstitution') as mock_constitution:
            mock_const_instance = MagicMock()
            mock_const_instance.get_constitution.return_value = "Constitution content"
            mock_constitution.return_value = mock_const_instance

            pm = LogosPromptManager()
            result = pm.get_constitution()

            assert result == "Constitution content"
            mock_const_instance.get_constitution.assert_called_once()

    def test_build_system_prompt_with_dual_context(self):
        """Test building system prompt with personality and technical context."""
        with patch('src.personality.prompt_manager.LogosConstitution') as mock_constitution:
            mock_const_instance = MagicMock()
            mock_const_instance.get_constitution.return_value = "Constitution content"
            mock_constitution.return_value = mock_const_instance

            pm = LogosPromptManager()

            personality_context = ["Personality memory 1", "Personality memory 2"]
            technical_context = ["Technical fact 1", "Technical fact 2"]

            prompt = pm.build_system_prompt(
                personality_context=personality_context,
                technical_context=technical_context
            )

            # Should include constitution
            assert "Constitution content" in prompt

            # Should include both types of context
            assert "Personality memory 1" in prompt
            assert "Personality memory 2" in prompt
            assert "Technical fact 1" in prompt
            assert "Technical fact 2" in prompt

            # Should have proper structure
            assert "PERSONALITY CONTEXT (Memories & Experiences):" in prompt
            assert "TECHNICAL CONTEXT (Knowledge & Facts):" in prompt

    def test_build_system_prompt_personality_only(self):
        """Test building system prompt with only personality context."""
        with patch('src.personality.prompt_manager.LogosConstitution') as mock_constitution:
            mock_const_instance = MagicMock()
            mock_const_instance.get_constitution.return_value = "Constitution"
            mock_constitution.return_value = mock_const_instance

            pm = LogosPromptManager()

            personality_context = ["Memory 1"]
            prompt = pm.build_system_prompt(personality_context=personality_context)

            assert "Constitution" in prompt
            assert "Memory 1" in prompt
            assert "PERSONALITY CONTEXT (Memories & Experiences):" in prompt
            assert "TECHNICAL CONTEXT (Knowledge & Facts):" not in prompt

    def test_build_system_prompt_technical_only(self):
        """Test building system prompt with only technical context."""
        with patch('src.personality.prompt_manager.LogosConstitution') as mock_constitution:
            mock_const_instance = MagicMock()
            mock_const_instance.get_constitution.return_value = "Constitution"
            mock_constitution.return_value = mock_const_instance

            pm = LogosPromptManager()

            technical_context = ["Fact 1"]
            prompt = pm.build_system_prompt(technical_context=technical_context)

            assert "Constitution" in prompt
            assert "Fact 1" in prompt
            assert "TECHNICAL CONTEXT (Knowledge & Facts):" in prompt
            assert "PERSONALITY CONTEXT (Memories & Experiences):" not in prompt

    def test_build_system_prompt_no_context(self):
        """Test building system prompt with no additional context."""
        with patch('src.personality.prompt_manager.LogosConstitution') as mock_constitution:
            mock_const_instance = MagicMock()
            mock_const_instance.get_constitution.return_value = "Constitution"
            mock_constitution.return_value = mock_const_instance

            pm = LogosPromptManager()

            prompt = pm.build_system_prompt()

            assert "Constitution" in prompt
            assert "PERSONALITY CONTEXT:" not in prompt
            assert "TECHNICAL CONTEXT:" not in prompt
            assert "NOTICE: No additional context provided" in prompt

    def test_build_system_prompt_backwards_compatibility(self):
        """Test backwards compatibility with old context_chunks parameter."""
        with patch('src.personality.prompt_manager.LogosConstitution') as mock_constitution:
            mock_const_instance = MagicMock()
            mock_const_instance.get_constitution.return_value = "Constitution"
            mock_constitution.return_value = mock_const_instance

            pm = LogosPromptManager()

            # Old API: context_chunks treated as technical context
            old_context = ["Old context 1", "Old context 2"]
            prompt = pm.build_system_prompt(context_chunks=old_context)

            assert "Constitution" in prompt
            assert "Old context 1" in prompt
            assert "Old context 2" in prompt
            assert "TECHNICAL CONTEXT (Knowledge & Facts):" in prompt  # Old context goes to technical

    def test_get_principles_summary(self):
        """Test getting principles summary."""
        with patch('src.personality.prompt_manager.LogosConstitution') as mock_constitution:
            mock_const_instance = MagicMock()
            mock_const_instance.get_principles_summary.return_value = "Summary of principles"
            mock_constitution.return_value = mock_const_instance

            pm = LogosPromptManager()
            summary = pm.get_principles_summary()

            assert summary == "Summary of principles"
            mock_const_instance.get_principles_summary.assert_called_once()

    def test_add_principle_delegates_to_constitution(self):
        """Test adding principle delegates to constitution."""
        with patch('src.personality.prompt_manager.LogosConstitution') as mock_constitution:
            mock_const_instance = MagicMock()
            mock_constitution.return_value = mock_const_instance

            pm = LogosPromptManager()
            pm.add_principle("New Principle", "Description")

            mock_const_instance.add_principle.assert_called_once_with("New Principle", "Description")

    def test_system_prompt_structure(self):
        """Test that system prompt has proper structure."""
        with patch('src.personality.prompt_manager.LogosConstitution') as mock_constitution:
            mock_const_instance = MagicMock()
            mock_const_instance.get_constitution.return_value = "Constitution text"
            mock_constitution.return_value = mock_const_instance

            pm = LogosPromptManager()

            prompt = pm.build_system_prompt(
                personality_context=["Memory"],
                technical_context=["Fact"]
            )

            # Should start with constitution
            assert prompt.startswith("LOGOS CONSTITUTION:")

            # Should have operational guidelines
            assert "OPERATIONAL GUIDELINES:" in prompt

            # Should have context sections
            assert "PERSONALITY CONTEXT (Memories & Experiences):" in prompt
            assert "TECHNICAL CONTEXT (Knowledge & Facts):" in prompt

            # Should end with guidelines
            assert "GUIDELINES:" in prompt