class Loggable():
    def __init__(self):
        self.log_data = []
    
    def append_log(self, memory: dict) -> None:
        if isinstance(memory, dict):
            if "role" in memory.keys() and "content" in memory.keys():
                self.log_data.append(memory)

    def extend_log(self, memory_list: list[dict]) -> None:
        for memory in memory_list:
            self.append_log(memory)

    def clear_log(self) -> None:
        self.log_data = []

    def get_last_log_entry(self, role: str=None) -> dict:
        if role is None:
            return self.log_data[-1]
        else:
            idx = -1
            while idx >= -len(self.log_data):
                if self.log_data[idx]["role"] == role:
                    return self.log_data[idx]
                idx -= 1
            return None
        
    def get_log(self) -> list[dict]:
        return self.log_data
    
    def erase_last_n_log_entries(self, n: int) -> None:
        self.log_data = self.log_data[0:-n]

    def __str__(self) -> str:
        result = "Log:\n"

        if len(self.log_data) == 0:
            result += "empty"
        else:
            result += "\n".join([str(memory_dict) for memory_dict in self.log_data])

        return result