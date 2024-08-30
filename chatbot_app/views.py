from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from users.views import JWTAuthentication
from chatbot_app.serializers import ChatListSerializer
from chatbot_app.openai_helper.chat_openai import send_chat_request_gpt
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from chathistory.views import save_chat, get_chats_by_user, create_new_chat, create_new_custom_chat, fetch_buttons
import json


@swagger_auto_schema(tags=["DeepLink"], method="POST")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def chats_by_user(request):
    data = request.data
    user_id = data['user_id']
    if not user_id:
        return Response("User Id is required", status=status.HTTP_400_BAD_REQUEST)
    response_list = get_chats_by_user(user_id=user_id)
    response = []
    for chat_message in response_list:
        response.append({
            "type": "client" if chat_message.is_user_message else "server",
            "message": chat_message.message,
            "createdAt": chat_message.datetime.strftime("%Y-%m-%d %H:%M:%S")
        })
    return Response(json.dumps(response), status=status.HTTP_200_OK)


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])
# def save_initial_server_thread(request):
#     serialized_chat_list = ChatListSerializer(data=request.data)
#     print("Receving call in backend")
#     if(serialized_chat_list.is_valid()):
#         ser_chat_list = serialized_chat_list.validated_data['chat_list']
#         user_id = serialized_chat_list.validated_data['user_id']
#         print("In clear chat")
#         print("Chat list: ", ser_chat_list)
#         for chat in ser_chat_list:
#             chat["is_user_message"] = False
#         save_chat(user_id, ser_chat_list)
#         return Response(json.dumps(True), status=status.HTTP_200_OK)
#     return Response(serialized_chat_list.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(tags=["DeepLink"], method="POST")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def chat_with_bot(request):
    serialized_chat_list = ChatListSerializer(data=request.data)
    if(serialized_chat_list.is_valid()):
        ser_chat_list = serialized_chat_list.validated_data['chat_list']
        user_id = serialized_chat_list.validated_data['user_id']
        
        # print("Data: ", request.data)
        is_custom_prompt = request.data['is_custom_prompt']
        custom_prompt = request.data['custom_prompt']
        
        
        # print("Is custom prompt: ", is_custom_prompt)
        # print("Custom Prompt: ", custom_prompt)
        
        extracted_list = []
        for chat in ser_chat_list:
            extracted_list.append({
                "type": chat["type"],
                "message": chat["message"]
            })
        gpt_chat_response = send_chat_request_gpt(extracted_list, is_custom_prompt, custom_prompt)
        save_chat_list = []
        # add recent chat of client with recent response of bot
        recent_client_message = extracted_list[-1]
        save_chat_list.extend([
            {
                "message": recent_client_message['message'],
                "datetime": datetime.now(),
                "is_user_message": True
            },
            {
                "message": gpt_chat_response,
                "datetime": datetime.now(),
                "is_user_message": False
            }
        ])
        save_chat(user_id, save_chat_list)
        return Response({
            "type": "server",
            "message": gpt_chat_response
        }, status=status.HTTP_200_OK)
    return Response(serialized_chat_list.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def clear_chat(request):
    user = request.user
    data = request.data
    chat_message = create_new_chat(user, data)
    # return Response({"message": "Chat cleared and saved."}, status=status.HTTP_200_OK)
    if chat_message:
        return Response(chat_message.data, status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "No new chat created"}, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def create_custom_chat(request):
    data = request.data
    user = request.user
    create_new_custom_chat(data, user)
    return Response({"message": "Custom chat created successfully"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_buttons(request):
    buttons_with_prompts = fetch_buttons(request.user)
    return Response(buttons_with_prompts, status=status.HTTP_200_OK)

