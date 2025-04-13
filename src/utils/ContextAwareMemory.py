from langchain.memory import ConversationBufferMemory

class ContextAwareMemory(ConversationBufferMemory):
    @property
    def memory_variables(self):
        return ["history", "context"]  # Trick LangChain into accepting both

    def load_memory_variables(self, inputs):
        base_memory = super().load_memory_variables(inputs)
        base_memory["context"] = inputs.get("context", "")  # Inject context from inputs
        return base_memory