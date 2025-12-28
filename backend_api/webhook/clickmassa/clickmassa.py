from fastapi import APIRouter

from src.global_state import state
from src.services.email import email

clickmassa_router = APIRouter()

@clickmassa_router.post("/message-alert")
def clickmassa_message_alert(
    request: dict
):
    try:
        state.logger.info(f"ClickMassa message alert triggered.")

        message = request.get('message', {})

        if not message:
            state.logger.warning("Message not found in the request.")
            return {"status_code": 400, "message": "Message not found in the request."}

        fromMe = message.get('fromMe', False)
        if fromMe:
            state.logger.info("Message is from the user, ignoring it.")
            return {"status_code": 200, "message": "ClickMassa message alert processed successfully."}
        
        isGroup = message.get('isGroup', False)
        if isGroup:
            state.logger.info("Message is from a group, ignoring it.")
            return {"status_code": 200, "message": "ClickMassa message alert processed successfully."}

        ticket = message.get('ticket', "Unknown")
        if ticket == "Unknown":
            state.logger.warning("User ID not found in the message.")
            return {"status_code": 400, "message": "User ID not found in the message."}
        
        user = ticket.get('user', "Unknown")
        if user == "Unknown":
            state.logger.warning("User not found in the ticket.")
            return {"status_code": 400, "message": "User not found in the ticket."}

        user_email = user.get('email', None)
        if not user_email:
            state.logger.warning("User email not found.")
            return {"status_code": 400, "message": "User email not found."}
        
        email(
            subject="ALERTA DE MENSAGEM CLICKMASSA",
            body=f"Nova mensagem recebida.\nVerifique o clickmassa assim que puder",
            to=user_email
        )

        state.logger.info("ClickMassa message alert processed successfully.")
        return {"status_code": 200, "message": "ClickMassa message alert processed successfully."}
    except Exception as e:
        state.logger.error(f"Failed to process ClickMassa message alert: {e}")
        return {"status_code": 500, "message": "Internal server error. Please try again later."}
