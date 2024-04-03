from odoo import models, api
import logging


_logger = logging.getLogger(__name__)


class HelpdeskAssistant(models.AbstractModel):
    _name = 'mail.thread'
    _inherit = 'mail.thread'

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None, custom_values=None):
        # Route the message like normal.
        routes = super(HelpdeskAssistant, self).message_route(
            message,
            message_dict,
            model=model,
            thread_id=thread_id,
            custom_values=custom_values
        )

        # Iterate the returned routes.
        for route in routes:
            # Upack the values in the route.
            model, thread_id, _, _, _ = route

            # Check whether the associated model is a helpdesk ticket, and check whether the thread ID is an integer.
            # Checking whether the thread ID is an integer is stronger than checking whether it exists.
            if model == 'helpdesk.ticket' and type(thread_id) is int:
                # Retrieve the helpdesk ticket directly using the thread ID.
                ticket = self.env['helpdesk.ticket'].browse(thread_id)

                # Check whether the helpdesk ticket exists, and check whether it is in the Solved stage.
                if ticket and ticket.stage_id.name == "Solved":
                    # Search for the stage ID by name.
                    stage = self.env['helpdesk.stage'].search([('name', '=', 'New Message')], limit=1)

                    # Check whether the stage exists.
                    if stage:
                        # Move the ticket to the Triage stage.
                        ticket.write({'stage_id': stage.id})

                        # Define the color index for red.
                        red_color_index = 1
                        # Change the color of the ticket to red.
                        ticket.color = red_color_index

                        # Write the event to the log.
                        _logger.info(f"helpdesk ticket {ticket.id} was moved to stage {stage.id}")

        # Return the routes like normal.
        return routes
