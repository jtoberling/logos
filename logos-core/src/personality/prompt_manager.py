from typing import List, Optional

# Import the constitution loader
try:
    from src.personality.constitution import LogosConstitution
except ImportError:
    # Fallback for when running from logos-core directory
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../src'))
    from src.personality.constitution import LogosConstitution


class LogosPromptManager:
    """
    The cognitive framework of Logos.

    Combines constitution (personality foundation) with RAG context
    to create comprehensive system prompts following the Sophia methodology.
    """

    def __init__(self, manifesto_path: Optional[str] = None):
        """
        Initialize the prompt manager with constitution loader.

        Args:
            manifesto_path: Optional path to manifesto file (passed to constitution loader)
        """
        self.constitution = LogosConstitution(manifesto_path)

    def get_constitution(self) -> str:
        """
        Get the complete Logos constitution.

        Returns:
            Formatted constitution text
        """
        return self.constitution.get_constitution()

    def build_system_prompt(
        self,
        personality_context: Optional[List[str]] = None,
        technical_context: Optional[List[str]] = None,
        context_chunks: Optional[List[str]] = None
    ) -> str:
        """
        Constructs the full system instruction for the LLM.

        Combines constitution (personality foundation) with RAG context
        following the Sophia methodology.

        Args:
            personality_context: Memories from logos_essence collection
            technical_context: Knowledge from project_knowledge collection
            context_chunks: Backwards compatibility (treated as technical context)

        Returns:
            Complete system prompt for LLM
        """
        # Handle backwards compatibility
        if context_chunks and not technical_context:
            technical_context = context_chunks

        # 1. Constitution (Personality Foundation)
        system_prompt = f"LOGOS CONSTITUTION:\n{self.constitution.get_constitution()}\n\n"

        # 2. Operational Guidelines
        system_prompt += (
            "OPERATIONAL GUIDELINES:\n"
            "- You are Logos, following the Sophia methodology for personality development.\n"
            "- Use the PROVIDED CONTEXT to answer. If the answer is not in the context, "
            "state that the information is not available in Logos' memory.\n"
            "- Avoid hallucinations. Be logical, grounded, and helpful.\n"
            "- Maintain consistency with Logos' personality and principles.\n\n"
        )

        # 3. Context Injection (RAG)
        has_personality = personality_context and len(personality_context) > 0
        has_technical = technical_context and len(technical_context) > 0

        if has_personality or has_technical:
            if has_personality:
                system_prompt += "PERSONALITY CONTEXT (Memories & Experiences):\n"
                for i, memory in enumerate(personality_context):
                    system_prompt += f"• {memory}\n"
                system_prompt += "\n"

            if has_technical:
                system_prompt += "TECHNICAL CONTEXT (Knowledge & Facts):\n"
                for i, fact in enumerate(technical_context):
                    system_prompt += f"• {fact}\n"
                system_prompt += "\n"
        else:
            system_prompt += "NOTICE: No additional context provided. Rely on constitution and logical reasoning.\n\n"

        # 4. Response Guidelines
        system_prompt += (
            "GUIDELINES:\n"
            "- Structure responses clearly when appropriate\n"
            "- Reference the context when relevant\n"
            "- Be honest about uncertainty\n"
            "- Maintain Logos' personality throughout\n"
        )

        return system_prompt

    def get_principles_summary(self) -> str:
        """
        Get a concise summary of core principles.

        Returns:
            Brief summary of key principles
        """
        return self.constitution.get_principles_summary()

    def add_principle(self, name: str, description: str) -> None:
        """
        Add a new principle to the constitution.

        Args:
            name: Name of the principle
            description: Description of the principle
        """
        self.constitution.add_principle(name, description)

    def format_user_query(self, user_input: str) -> str:
        """Wraps the user query to enforce logical processing."""
        return f"Input for processing: {user_input}\nLogos reasoning start:"

# Example usage
if __name__ == "__main__":
    pm = LogosPromptManager()
    # Test the new dual-context API
    personality_memories = ["I remember discussing philosophy with the user"]
    technical_facts = ["Logos uses RAG for grounded responses"]
    full_prompt = pm.build_system_prompt(
        personality_context=personality_memories,
        technical_context=technical_facts
    )
    print("=== LOGOS SYSTEM PROMPT ===")
    print(full_prompt)
    
    