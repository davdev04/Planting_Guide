try:
    from langchain_classic.prompts import PromptTemplate
except ImportError:  # pragma: no cover - newer LangChain installs use langchain_core
    from langchain_core.prompts import PromptTemplate

template = PromptTemplate(
    input_variables=["name", "planting_age"],
    template="""
You are a gardening assistant.
Given the plant name "{name}" and planting age "{planting_age}",
suggest an optimal planting date to suit seasonal conditions in Brisbane, Australia,
in YYYY-MM-DD format.
"""
)