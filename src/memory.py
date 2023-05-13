class Memory():
    def __init__(self):
        self.memory_data = []
    
    def append_memory(self, memory: dict) -> None:
        if isinstance(memory, dict):
            if "role" in memory.keys() and "content" in memory.keys():
                self.memory_data.append(memory)

    def extend_memory(self, memory_list: list[dict]) -> None:
        for memory in memory_list:
            self.append_memory(self, memory)

    def __str__(self) -> str:
        return "\n".join(self.memory_data)