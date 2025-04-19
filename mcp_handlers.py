import os
from service_manager import MCPManager

# Initialize manager and connect services
mcp = MCPManager()

mcp.connect_server("whatsapp", os.getenv("WHATSAPP_MCP"), {
    "Authorization": f"Bearer {os.getenv('WHATSAPP_API_KEY')}"
})
mcp.connect_server("gdrive", os.getenv("GDRIVE_MCP"), {
    "Authorization": f"Bearer {os.getenv('GDRIVE_TOKEN')}"
})
mcp.connect_server("gsuite", os.getenv("GSUITE_MCP"), {
    "Authorization": f"Bearer {os.getenv('GSUITE_TOKEN')}"
})

def send_message_via_whatsapp(phone, message):
    return mcp.get_server("whatsapp").send_message(phone, message)

def search_drive(query):
    return mcp.get_server("gdrive").search_files(query)

def schedule_event(details):
    return mcp.get_server("gsuite").create_calendar_event(details)

def send_email(details):
    return mcp.get_server("gsuite").send_email(
        to=details['to'],
        subject=details['subject'],
        body=details['body']
    )