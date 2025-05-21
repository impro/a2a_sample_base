from ADK.discovery import AgentRegistry
from ADK.collab import CollaborationManager
from ADK.ux_nego import UXNegotiator
from ADK.task_management import TaskManager
from representation.syntax import render_list_images, render_markdown, render_list, render_card, render_table

class AsterAgent:
    capabilities = ['orchestrate', 'render']
    def __init__(self, registry):
        self.registry = registry
        self.collab = CollaborationManager()
        self.ux_nego = UXNegotiator()
        self.task_manager = TaskManager()

    def receive(self, from_user, user_input):
        # 1. Discovery
        domain_agents = self.registry.discover('search')
        domain_agent = domain_agents[0]
        # 2. Collab
        result = self.collab.send(self, domain_agent, user_input)
        # 3. UX Nego
        desired_repr = result.get('desired_representation', 'list_images') #<--
        repr_type = self.ux_nego.negotiate(domain_agent, desired_repr)
        # 4. Task Management + 5. Representation
        rendered = self.task_manager.assign(self, 'render', {'data': result['data'], 'repr': repr_type}) #<--
        return rendered

    def handle_task(self, task, args):
        if task == 'render':
            data, repr_type = args['data'], args['repr']
            if repr_type == "list_images":
                return render_list_images(data)
            elif repr_type == "markdown":
                return render_markdown(data)
            elif repr_type == "list":
                return render_list(data)
            elif repr_type == "card":
                return render_card(data)
            elif repr_type == "table":
                return render_table(data)
            else:
                return data