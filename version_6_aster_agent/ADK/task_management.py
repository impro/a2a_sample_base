class TaskManager:
    def assign(self, agent, task, args):
        return agent.handle_task(task, args)